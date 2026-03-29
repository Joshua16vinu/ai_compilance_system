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

def process_pdf_v2(pdf_path: str):

    embedder = load_embedding_model()

    raw_text = extract_text_from_pdf(pdf_path)

    if not raw_text.strip():
        raise ValueError("No text extracted from PDF")

    cleaned_text = clean_text(raw_text)

    chunks = sentence_token_chunking(cleaned_text)

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

        # 🔹 2. Retrieve NIST (domain filtered)
        candidates = retrieve_nist_for_chunk_domains(chunk, domains, top_k=5)

        # 🔹 3. Rerank
        ranked = rerank_results(chunk, candidates)

        # 🔹 4. Dynamic selection
        top_nist = select_top_dynamic(ranked)

        # 🔹 5. Assign to EACH domain
        for d in domains:

            entry = {
                "input": chunk,
                "domain_scores": domain_info["scores"],
                "nist_chunks": []
            }

            for n in top_nist:

                # ✅ relaxed domain match
                if n["metadata"].get("domain") in domains:

                    entry["nist_chunks"].append({
                        "id": n["id"],
                        "text": n["text"],
                        "score": n["score"],
                        "rerank_score": n.get("rerank_score", 0)
                    })

            final_output[d].append(entry)

    # ============================================================
    # 🔥 FINAL: MAKE NIST UNIQUE PER DOMAIN
    # ============================================================

    for domain, items in final_output.items():

        unique_map = {}

        # collect best version
        for item in items:
            for n in item["nist_chunks"]:

                if n["id"] not in unique_map:
                    unique_map[n["id"]] = n
                else:
                    if n["rerank_score"] > unique_map[n["id"]]["rerank_score"]:
                        unique_map[n["id"]] = n

        used_ids = set()

        # redistribute (unique per domain)
        for item in items:
            new_nist = []

            for n in item["nist_chunks"]:
                if n["id"] not in used_ids:
                    new_nist.append(unique_map[n["id"]])
                    used_ids.add(n["id"])

            item["nist_chunks"] = new_nist

    # ============================================================
    # 🔹 METRICS (DEBUG)
    # ============================================================

    for domain, items in final_output.items():

        total_input = len(items)
        total_nist = sum(len(i["nist_chunks"]) for i in items)

        print(f"\n📌 {domain}")
        print(f"Input chunks: {total_input}")
        print(f"NIST chunks: {total_nist}")

    return final_output