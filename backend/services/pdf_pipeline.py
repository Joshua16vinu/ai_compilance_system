from backend.ocr.pdf_loader import extract_text_from_pdf
from backend.ocr.text_cleaner import clean_text
from backend.chunking.domain_chunker import chunk_by_domain
from backend.services.nist_retrieval import retrieve_nist_for_chunks
from backend.chunking.input_text_chunking import sentence_token_chunking
from backend.embeddings.embedding_model import load_embedding_model
from backend.domain.domain_classification import classify_chunk_domains
from backend.services.nist_retrieval import retrieve_nist_for_chunk_domains
from backend.reranker_model.reranker_loader import load_reranker
from backend.services.nist_retrieval import select_top_dynamic
from collections import defaultdict
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

# def process_pdf_v2(pdf_path: str):
#     """
#     New Pipeline:
#     PDF → Extract → Clean → Token Chunk → Select → Retrieve NIST
#     """

#     # 1. Extract text
#     raw_text = extract_text_from_pdf(pdf_path)

#     if not raw_text.strip():
#         raise ValueError("No text extracted from PDF")

#     # 2. Clean
#     cleaned_text = clean_text(raw_text)

#     # 3. Chunking (150–250 tokens)
#     chunks = sentence_token_chunking(cleaned_text)
#     print(chunks)

#     print(f"✅ Total chunks created: {len(chunks)}")

#     # 4. Select top chunks (simple heuristic for now)
#     selected_chunks = sorted(chunks, key=len, reverse=True)

#     print(f"✅ Selected top {len(selected_chunks)} chunks")

#     # 5. Retrieve NIST (3–5 per chunk)
#     nist_results = retrieve_nist_for_chunks(
#         selected_chunks,
#         top_k=5
#     )
#     print(nist_results)

#     print(f"✅ Retrieved {len(nist_results)} NIST records")

#     return {
#         "chunks": selected_chunks,
#         "nist": nist_results  # final filtered
#     }

def rerank_results(chunk, candidates):

    reranker = load_reranker()

    pairs = [(chunk, c["text"]) for c in candidates]

    scores = reranker.predict(pairs)

    for i, s in enumerate(scores):
        candidates[i]["rerank_score"] = float(s)

    ranked = sorted(candidates, key=lambda x: x["rerank_score"], reverse=True)

    return ranked   # ✅ no slicing


def make_unique_and_distribute(final_output, max_per_chunk=5):

    for domain, items in final_output.items():

        if not items:
            continue

        # 🔹 Step 1: Collect ALL NIST (no duplicates)
        unique_nist = {}

        for item in items:
            for n in item["nist_chunks"]:
                unique_nist[n["id"]] = n   # overwrite → keeps unique only

        # 🔹 Step 2: Reset chunks
        for item in items:
            item["nist_chunks"] = []

        all_nist = list(unique_nist.values())

        # 🔹 Step 3: Distribute (round-robin)
        i = 0
        for n in all_nist:
            idx = i % len(items)

            if len(items[idx]["nist_chunks"]) < max_per_chunk:
                items[idx]["nist_chunks"].append(n)

            i += 1


# ============================================================
# 🔹 MAIN PIPELINE
# ============================================================

def process_pdf_v2(pdf_path: str):

    embedder = load_embedding_model()

    raw_text = extract_text_from_pdf(pdf_path)

    if not raw_text.strip():
        raise ValueError("No text extracted from PDF")

    cleaned_text = clean_text(raw_text)

    chunks = sentence_token_chunking(cleaned_text)
    print(f"✅ Total chunks created: {len(chunks)}")
    final_output = {
        "ISMS": [],
        "Risk Management": [],
        "Patch Management": [],
        "Data Privacy & Security": []
    }

    for chunk in chunks:

    # 🔹 1. Domain classification
     domain_info = classify_chunk_domains(chunk, embedder)
     domains = domain_info["domains"]

     print("Domains:", domains)

    # 🔹 2. Process EACH domain separately
     for d in domains:

        # ✅ Retrieve per domain
        candidates = retrieve_nist_for_chunk_domains(
             chunk,
              domains=[d],
              top_k=15
)

        print(len(candidates), "candidates for domain", d)

        # 🔹 3. Select top 5
        top_nist = candidates[:5]

        entry = {
            "input": chunk,
            "domain_scores": domain_info["scores"],
            "nist_chunks": []
        }

        # 🔹 4. Assign (NO NEED to filter now)
        for n in top_nist:
            entry["nist_chunks"].append({
                "id": n["id"],
                "text": n["text"],
                "score": n["score"],
            })

        final_output[d].append(entry)

    # ============================================================
    # 🔥 APPLY UNIQUE + BALANCED DISTRIBUTION
    # ============================================================

    make_unique_and_distribute(final_output)

    # ============================================================
    # 🔹 METRICS
    # ============================================================

    for domain, items in final_output.items():
        total_input = len(items)
        total_nist = sum(len(i["nist_chunks"]) for i in items)

        print(f"\n📌 {domain}")
        print(f"Input chunks: {total_input}")
        print(f"NIST chunks: {total_nist}")

    return final_output