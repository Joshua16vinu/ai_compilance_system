"""
Test script to verify gap analysis functionality without running the Flask server.
This simulates what happens when the /api/upload-pdf endpoint is called.
"""
import sys
import os
from pathlib import Path
import requests
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# Add parent directory to path BEFORE any imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.ocr.text_cleaner import clean_text
from backend.ocr.pdf_loader import extract_text_from_pdf


def estimate_tokens(text: str) -> int:
    """
    Rough estimate of tokens (approximation: ~1 token per 4 characters).
    
    Args:
        text: Text to estimate token count for
        
    Returns:
        Estimated token count
    """
    return len(text) // 4


def create_batches_with_overlap(text: str, batch_tokens: int = 300, overlap_percent: float = 0.2):
    """
    Split text into batches with fixed token size and overlap.
    
    Args:
        text: Text to split into batches
        batch_tokens: Number of tokens per batch (default: 300)
        overlap_percent: Overlap percentage between batches (default: 0.2 = 20%)
        
    Yields:
        Tuples of (batch_number, batch_text, batch_info)
    """
    # Calculate character size based on token estimation
    chars_per_token = 4
    batch_chars = batch_tokens * chars_per_token
    overlap_chars = int(batch_chars * overlap_percent)
    
    text_length = len(text)
    batch_num = 0
    position = 0
    
    while position < text_length:
        # Calculate end position for this batch
        end_pos = min(position + batch_chars, text_length)
        
        # Extract batch text
        batch_text = text[position:end_pos]
        
        # Keep track of next position (with overlap)
        if end_pos < text_length:
            position = end_pos - overlap_chars
        else:
            position = end_pos
        
        batch_num += 1
        batch_info = {
            "batch_num": batch_num,
            "chars": len(batch_text),
            "est_tokens": estimate_tokens(batch_text),
            "position": position
        }
        
        yield batch_num, batch_text, batch_info


def call_ollama_local(text: str, model: str = "mistral", system_prompt: str = None):
    """
    Call local Ollama model with the given text.
    
    Args:
        text: Text to send to the model
        model: Model name to use (default: mistral)
        system_prompt: Optional system prompt
        
    Returns:
        Model response or None if failed
    """
    try:
        url = "http://localhost:11434/api/generate"
        
        payload = {
            "model": model,
            "prompt": text,
            "stream": False
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            return result.get("response", "")
        else:
            print(f"⚠️  Ollama request failed with status {response.status_code}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("⚠️  Could not connect to Ollama. Is it running? (ollama serve)")
        return None
    except Exception as e:
        print(f"⚠️  Ollama error: {e}")
        return None


def process_batch_parallel(batch_info: dict, model: str = "mistral"):
    """
    Process a single batch with Ollama (for parallel execution).
    
    Args:
        batch_info: Dict with batch_num and text
        model: Model to use
        
    Returns:
        Dict with batch result or error
    """
    batch_num = batch_info["batch_num"]
    batch_text = batch_info["text"]
    
    start_time = time.time()
    
    try:
        response = call_ollama_local(
            batch_text,
            model=model,
            system_prompt="You are a compliance analyst. Analyze this text and identify key compliance points."
        )
        
        elapsed = time.time() - start_time
        
        return {
            "batch_num": batch_num,
            "text": batch_text,
            "response": response,
            "status": "success" if response else "no_response",
            "start_time": start_time,
            "elapsed_time": elapsed
        }
    except Exception as e:
        elapsed = time.time() - start_time
        return {
            "batch_num": batch_num,
            "text": batch_text,
            "response": None,
            "status": "error",
            "error": str(e),
            "start_time": start_time,
            "elapsed_time": elapsed
        }



def test_gap_analysis(pdf_path: str):
    """
    Test the complete gap analysis pipeline with local Ollama model.
    
    Args:
        pdf_path: Path to the PDF file to analyze
    """
    from datetime import datetime
    print("Started test_gap_analysis at", datetime.now())
    print("=" * 80)
    print("TESTING GAP ANALYSIS PIPELINE WITH OLLAMA BATCHING")
    print("=" * 80)
    print(f"\nProcessing: {pdf_path}")
    print("\n" + "-" * 80)
    
    # Step 1: Process PDF (OCR + Domain Chunking)
    print("\n[STEP 1] Processing PDF...")
    try:
        raw_text = extract_text_from_pdf(pdf_path)

        if not raw_text.strip():
            raise ValueError("No text extracted from PDF")
        
        cleaned_text = clean_text(raw_text)
        
        print(f"✅ Extracted {len(raw_text)} characters of raw text")
        print(f"✅ Cleaned text length: {len(cleaned_text)} characters")
        print(f"✅ Estimated tokens: ~{estimate_tokens(cleaned_text)}")
        
    except Exception as e:
        print(f"❌ PDF processing failed: {e}")
        return
    
    # Step 2: Process in batches with Ollama (in parallel)
    print("\n" + "-" * 80)
    print("\n[STEP 2] Processing batches with Ollama in PARALLEL (300 tokens, 20% overlap)...")
    
    batch_results = []
    
    try:
        # First, collect all batches
        batches = []
        for batch_num, batch_text, batch_info in create_batches_with_overlap(
            cleaned_text, batch_tokens=300, overlap_percent=0.2
        ):
            batches.append({
                "batch_num": batch_num,
                "text": batch_text,
                "est_tokens": batch_info['est_tokens'],
                "chars": batch_info['chars']
            })
        
        print(f"\nPrepared {len(batches)} batches for parallel processing")
        print(f"Max workers: 3 (adjust as needed for your system)")
        
        # Record start time for parallel execution
        parallel_start = time.time()
        
        # Process batches in parallel
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {executor.submit(process_batch_parallel, batch, "mistral"): batch for batch in batches}
            
            completed = 0
            for future in as_completed(futures):
                completed += 1
                batch = futures[future]
                
                try:
                    result = future.result()
                    batch_num = result["batch_num"]
                    
                    print(f"\n  ✅ Batch {batch_num}: {result['status']}")
                    print(f"    - Tokens: ~{batch['est_tokens']}")
                    print(f"    - Characters: {batch['chars']}")
                    print(f"    - Time to complete: {result['elapsed_time']:.2f}s")
                    
                    if result['response']:
                        # Print full response
                        print(f"    - Full Response:\n{result['response']}")
                    
                    batch_results.append(result)
                    
                except Exception as e:
                    print(f"\n  ❌ Batch {batch['batch_num']} failed: {e}")
        
        parallel_elapsed = time.time() - parallel_start
        
        # Sort results by batch number
        batch_results.sort(key=lambda x: x["batch_num"])
        
        print(f"\n✅ Processed {len(batch_results)} batches successfully in parallel")
        
    except Exception as e:
        print(f"❌ Batch processing failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Step 3: Save results
    print("\n" + "-" * 80)
    print("\n[STEP 3] Saving batch results...")
    
    try:
        output_dir = Path(__file__).resolve().parents[1] / "backend" / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"ollama_batch_results_{timestamp}.json"
        
        # Prepare output (include full responses and timing info)
        output_data = {
            "timestamp": timestamp,
            "processing_mode": "parallel",
            "max_workers": 3,
            "total_batches": len(batch_results),
            "total_tokens": estimate_tokens(cleaned_text),
            "total_time_seconds": parallel_elapsed,
            "batches": [
                {
                    "batch_num": r["batch_num"],
                    "status": r["status"],
                    "response": r["response"] if r["response"] else "No response",
                    "elapsed_time": r.get("elapsed_time", 0),
                    "start_time": r.get("start_time", 0)
                }
                for r in batch_results
            ]
        }
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2)
        
        print(f"✅ Results saved to: {output_file}")
        
        # Print summary
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"\nTotal batches processed: {len(batch_results)}")
        print(f"Total tokens: ~{estimate_tokens(cleaned_text)}")
        print(f"Batch size: 300 tokens with 20% overlap")
        print(f"Processing mode: PARALLEL (3 workers)")
        print(f"\n⏱️  TIMING ANALYSIS:")
        print(f"   - Total parallel execution time: {parallel_elapsed:.2f}s")
        
        # Calculate sum of individual batch times
        total_batch_time = sum(r.get("elapsed_time", 0) for r in batch_results)
        print(f"   - Sum of individual batch times: {total_batch_time:.2f}s")
        
        # If parallel time is much less than sum of batch times, it's parallel
        if total_batch_time > 0:
            speedup = total_batch_time / parallel_elapsed
            print(f"   - Speedup factor: {speedup:.2f}x (>1.5x indicates parallel execution)")
            if speedup > 1.5:
                print(f"   ✅ CONFIRMED: Running in parallel!")
            else:
                print(f"   ⚠️  WARNING: Appears to be sequential or limited parallelism")
        
        print(f"\nPer-batch timing:")
        for r in batch_results:
            print(f"  - Batch {r['batch_num']}: {r.get('elapsed_time', 0):.2f}s")
        
        # Count by status
        statuses = {}
        for r in batch_results:
            status = r.get("status", "unknown")
            statuses[status] = statuses.get(status, 0) + 1
        
        print(f"\nBatch status breakdown:")
        for status, count in sorted(statuses.items()):
            print(f"  - {status}: {count}")
        
        # Show first successful response
        successful = [r for r in batch_results if r["response"]]
        if successful:
            print(f"\nFirst batch full response:")
            response = successful[0]["response"]
            print(response[:500] if len(response) > 500 else response)
        
        print("\n" + "=" * 80)
        print("✅ TEST COMPLETED SUCCESSFULLY")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Results saving failed: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        from datetime import datetime
        print("\nFinished test_gap_analysis at", datetime.now())


if __name__ == "__main__":    
    base_dir = Path(__file__).resolve().parents[1]
    
    test_pdf = base_dir / "policies" / "Policy_1.pdf"
    
    if not test_pdf.exists():
        print(f"❌ PDF file not found: {test_pdf}")
        print("\nPlease update the pdf_path in this script to point to a valid PDF file.")
        sys.exit(1)
    
    test_gap_analysis(str(test_pdf))
