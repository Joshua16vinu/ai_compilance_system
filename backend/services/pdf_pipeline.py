from backend.ocr.pdf_loader import extract_text_from_pdf
from backend.ocr.text_cleaner import clean_text
from backend.chunking.domain_chunker import chunk_by_domain
from backend.services.nist_retrieval import retrieve_nist_for_chunks
from backend.chunking.input_text_chunking import sentence_token_chunking
def process_pdf(pdf_path: str):
    """
    Complete PDF → OCR → Clean → Domain Chunk pipeline
    """
    raw_text = extract_text_from_pdf(pdf_path)

    if not raw_text.strip():
        raise ValueError("No text extracted from PDF")

    cleaned_text = clean_text(raw_text)
    print(f"Cleaned text:\n{cleaned_text}")
    chunks = chunk_by_domain(cleaned_text)
    print(f"Extracted {len(chunks)} domain-specific chunks from PDF")
    print("pdf pipeline completed")
    return chunks



#version 2

def process_pdf_v2(pdf_path: str):
    """
    New Pipeline:
    PDF → Extract → Clean → Token Chunk → Select → Retrieve NIST
    """

    # 1. Extract text
    raw_text = extract_text_from_pdf(pdf_path)

    if not raw_text.strip():
        raise ValueError("No text extracted from PDF")

    # 2. Clean
    cleaned_text = clean_text(raw_text)

    # 3. Chunking (150–250 tokens)
    chunks = sentence_token_chunking(cleaned_text)
    print(chunks)

    print(f"✅ Total chunks created: {len(chunks)}")

    # 4. Select top chunks (simple heuristic for now)
    selected_chunks = sorted(chunks, key=len, reverse=True)

    print(f"✅ Selected top {len(selected_chunks)} chunks")

    # 5. Retrieve NIST (3–5 per chunk)
    nist_results = retrieve_nist_for_chunks(
        selected_chunks,
        top_k=5
    )
    print(nist_results)

    print(f"✅ Retrieved {len(nist_results)} NIST records")

    return {
        "chunks": selected_chunks,
        "nist": nist_results  # final filtered
    }