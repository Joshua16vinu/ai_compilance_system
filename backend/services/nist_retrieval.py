from pathlib import Path
from chromadb import PersistentClient
from backend.embeddings.embedding_model import load_embedding_model

# Paths
BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "backend" / "db" / "chroma"
COLLECTION_NAME = "nist_controls"

_client = PersistentClient(path=str(DB_PATH))
_collection = _client.get_collection(name=COLLECTION_NAME)


def fetch_related_nist_records(subdomain: str, domain: str = None, top_k: int = 3):
    """
    Fetch related NIST records from ChromaDB based on subdomain.
    Uses metadata filtering to find exact subdomain matches.
    
    Args:
        subdomain: The subdomain to search for
        domain: Optional domain filter
        top_k: Maximum number of records to return
        
    Returns:
        List of dictionaries with 'id', 'text', 'metadata'
    """
    collection = _collection

    
    # Build where clause
    where_clause = {"subdomain": subdomain}
    if domain:
        where_clause["domain"] = domain
    
    results = collection.get(
        where=where_clause,
        include=["documents", "metadatas"],
        limit=top_k
    )
    
    # Format results
    records = []
    ids = results.get("ids", [])
    documents = results.get("documents", [])
    metadatas = results.get("metadatas", [])
    
    for i, (doc_id, doc, meta) in enumerate(zip(ids, documents, metadatas)):
        records.append({
            "id": doc_id,
            "text": doc,
            "metadata": meta
        })
    
    return records


def fetch_similar_nist_records(policy_text: str, subdomain: str = None, top_k: int = 3):
    """
    Fetch similar NIST records using semantic search.
    
    Args:
        policy_text: The organization policy text to compare
        subdomain: Optional subdomain filter
        top_k: Number of similar records to return
        
    Returns:
        List of dictionaries with 'id', 'text', 'metadata', 'similarity'
    """
    embedder = load_embedding_model()
    collection = _collection

    
    # Create embedding for the input policy text
    query_embedding = embedder.encode(policy_text).tolist()
    
    # Build query
    query_params = {
        "query_embeddings": [query_embedding],
        "n_results": top_k,
        "include": ["documents", "metadatas", "distances"]
    }
    
    # Optionally filter by subdomain
    if subdomain:
        query_params["where"] = {"subdomain": subdomain}
    
    results = collection.query(**query_params)
    
    # Format results
    records = []
    sim_ids = results.get("ids", [[]])[0]
    sim_documents = results.get("documents", [[]])[0]
    sim_metadatas = results.get("metadatas", [[]])[0]
    sim_distances = results.get("distances", [[]])[0]
    
    for doc_id, doc, meta, dist in zip(sim_ids, sim_documents, sim_metadatas, sim_distances):
        similarity = 1 - dist  # Convert distance to similarity
        records.append({
            "id": doc_id,
            "text": doc,
            "metadata": meta,
            "similarity": similarity
        })
    
    return records


def format_nist_chunks_for_prompt(records: list) -> str:
    """
    Format NIST records into a readable text block for the LLM prompt.
    
    Args:
        records: List of record dictionaries
        
    Returns:
        Formatted string of NIST chunks
    """
    if not records:
        return "No relevant NIST controls found for this subdomain."
    
    formatted = []
    for i, record in enumerate(records, 1):
        meta = record.get("metadata", {})
        text = record.get("text", "")
        
        chunk = f"--- NIST Control #{i} ---\n"
        chunk += f"Source: {meta.get('source_file', 'Unknown')}\n"
        chunk += f"Domain: {meta.get('domain', 'N/A')}\n"
        chunk += f"Subdomain: {meta.get('subdomain', 'N/A')}\n"
        
        # Add similarity score if available
        if "similarity" in record:
            chunk += f"Similarity: {record['similarity']:.4f}\n"
        
        chunk += f"\nText:\n{text}\n"
        formatted.append(chunk)
    
    return "\n\n".join(formatted)

def extract_query_keywords(query: str):
    return [w.lower() for w in query.split() if len(w) > 2]

def keyword_search(query: str, top_k: int = 5, domain=None):
    query_keywords = extract_query_keywords(query)

    all_data = _collection.get(include=["documents", "metadatas"])

    records = []

    for doc_id, doc, meta in zip(
        all_data["ids"],
        all_data["documents"],
        all_data["metadatas"]
    ):
        # 🔥 STRICT DOMAIN FILTER FIRST
        if domain and meta.get("domain") != domain:
            continue

        text = doc.lower()

        match_score = sum(1 for q in query_keywords if q in text)

        if match_score > 0:
            records.append({
                "id": doc_id,
                "text": doc,
                "metadata": meta,
                "score": match_score,
                "source": "keyword"
            })

    records = sorted(records, key=lambda x: x["score"], reverse=True)

    return records[:top_k]

def hybrid_fetch_nist_records(policy_text: str, domain: str = None):
    embedder = load_embedding_model()

    # 🔹 Semantic (top 10)
    query_embedding = embedder.encode(policy_text).tolist()

    query_params = {
        "query_embeddings": [query_embedding],
        "n_results": 10,
        "include": ["documents", "metadatas", "distances"]
    }

    if domain:
        query_params["where"] = {"domain": domain}

    semantic_results = _collection.query(**query_params)

    combined = {}

    # Add semantic
    for doc_id, doc, meta, dist in zip(
        semantic_results["ids"][0],
        semantic_results["documents"][0],
        semantic_results["metadatas"][0],
        semantic_results["distances"][0]
    ):
        similarity = 1 - dist

        combined[doc_id] = {
            "id": doc_id,
            "text": doc,
            "metadata": meta,
            "score": similarity
        }
    #print(f"\n📌 Semantic Results Count: {len(semantic_results['ids'][0])}")
    # 🔹 Keyword (top 5)
    keyword_results = keyword_search(policy_text, top_k=5)
    #print(f"\n📌 Keyword Results Count: {len(keyword_results)}")
    for r in keyword_results:
        if r["id"] in combined:
            combined[r["id"]]["score"] += r["score"]
        else:
            combined[r["id"]] = r
    
    #print("\n🔗 Merging Semantic + Keyword Results (UNION)")
    #print(f"\n📊 Total Combined Chunks: {len(combined)}")
    # 🔹 Sort final
    final_results = sorted(combined.values(), key=lambda x: x["score"], reverse=True)
    
    return final_results[:10]



# def hybrid_fetch_nist_records_version2(policy_text: str, domain: str = None,top_k: int = 5):
#     embedder = load_embedding_model()

#     # 🔹 Semantic (top 10)
#     query_embedding = embedder.encode(policy_text).tolist()

#     query_params = {
#         "query_embeddings": [query_embedding],
#         "n_results": top_k,
#         "include": ["documents", "metadatas", "distances"]
#     }

#     if domain:
#         query_params["where"] = {"domain": domain}

#     semantic_results = _collection.query(**query_params)

#     combined = {}

#     # Add semantic
#     for doc_id, doc, meta, dist in zip(
#         semantic_results["ids"][0],
#         semantic_results["documents"][0],
#         semantic_results["metadatas"][0],
#         semantic_results["distances"][0]
#     ):
#         similarity = 1 - dist

#         combined[doc_id] = {
#             "id": doc_id,
#             "text": doc,
#             "metadata": meta,
#             "score": similarity
#         }
#     #print(f"\n📌 Semantic Results Count: {len(semantic_results['ids'][0])}")
#     # 🔹 Keyword (top 5)
#     keyword_results = keyword_search(policy_text, top_k=5)
#     #print(f"\n📌 Keyword Results Count: {len(keyword_results)}")
#     for r in keyword_results:
#         if r["id"] in combined:
#             combined[r["id"]]["score"] += r["score"]
#         else:
#             combined[r["id"]] = r
    
#     #print("\n🔗 Merging Semantic + Keyword Results (UNION)")
#     #print(f"\n📊 Total Combined Chunks: {len(combined)}")
#     # 🔹 Sort final
#     final_results = sorted(combined.values(), key=lambda x: x["score"], reverse=True)
    
#     return final_results[:top_k]


def hybrid_fetch_nist_records_version2(policy_text, domain=None, top_k=5):
    embedder = load_embedding_model()

    query_embedding = embedder.encode(policy_text).tolist()

    query_params = {
        "query_embeddings": [query_embedding],
        "n_results": top_k,
        "include": ["documents", "metadatas", "distances"]
    }

    if domain:
        query_params["where"] = {"domain": domain}

    semantic_results = _collection.query(**query_params)

    combined = {}

    # Semantic
    for doc_id, doc, meta, dist in zip(
        semantic_results["ids"][0],
        semantic_results["documents"][0],
        semantic_results["metadatas"][0],
        semantic_results["distances"][0]
    ):
        similarity = 1 - dist

        combined[doc_id] = {
            "id": doc_id,
            "text": doc,
            "metadata": meta,
            "score": similarity
        }

    keyword_results = keyword_search(
    policy_text,
    top_k=5,
    domain=domain   # 🔥 PASS DOMAIN HERE
)
   

# 🔥 FILTER HERE
    

    for r in keyword_results:
        if r["id"] in combined:
            combined[r["id"]]["score"] += r["score"]
        else:
            combined[r["id"]] = r

    final_results = sorted(combined.values(), key=lambda x: x["score"], reverse=True)

    return final_results[:top_k]

def extract_relevant_text(records, query):
    #print("\n✂️ [STEP 2] Sentence Extraction Started")
    embedder = load_embedding_model()
    query_embedding = embedder.encode(query)

    query_words = query.lower().split()
    extracted = []
    total_sentences = 0
    matched_sentences = 0
    for r in records:
     sentences = r["text"].split(".")
     total_sentences += len(sentences)

     for s in sentences:
        s_clean = s.strip()

        if len(s_clean) < 10:
            continue

        keyword_match = any(q in s_clean.lower() for q in query_words)

        sentence_embedding = embedder.encode(s_clean)
        similarity = sum(a*b for a, b in zip(query_embedding, sentence_embedding))

        if keyword_match or similarity > 0.5:
            matched_sentences += 1
            #print(f"✅ Matched: {s_clean[:80]}... | Score: {similarity:.4f}")
            extracted.append((s_clean, similarity))

    extracted = sorted(extracted, key=lambda x: x[1], reverse=True)
    #print(f"\n📊 Total Sentences Scanned: {total_sentences}")
    #print(f"📊 Matched Sentences: {matched_sentences}")
    return [s for s, _ in extracted[:20]]




def retrieve_nist_for_chunks(chunks, top_k=5):
    """
    Retrieve NIST chunks for each input chunk
    """

    all_results = []

    for chunk in chunks:
        results = hybrid_fetch_nist_records_version2(
            policy_text=chunk,
            top_k=top_k
        )
        all_results.extend(results)

    # Deduplicate
    unique = {r["id"]: r for r in all_results}

    # Global ranking
    ranked = sorted(unique.values(), key=lambda x: x["score"], reverse=True)
    print(f"\n📌 Total NIST Records Retrieved (Pre-Dedup): {len(all_results)}"  )
    print(f"\n📌 Total NIST Records Retrieved (Post-Dedup): {len(ranked)}"  )

    return ranked

def select_top_dynamic(ranked, min_score=-5.0, max_k=3, score_gap=3.0):

    if not ranked:
        return []

    selected = [ranked[0]]

    for i in range(1, len(ranked)):
        current = ranked[i]
        prev = ranked[i - 1]

        # gap check
        # if prev["rerank_score"] - current["rerank_score"] > score_gap:
        #     break

        # relaxed threshold
        if current["rerank_score"] < min_score:
            continue   # 🔥 skip instead of break

        selected.append(current)

        if len(selected) >= max_k:
            break

    return selected

def retrieve_nist_for_chunk_domains(chunk, domains, top_k=15):
    all_results = []

    for domain in domains:
        results = hybrid_fetch_nist_records_version2(
            policy_text=chunk,
            domain=domain,
            top_k=top_k
        )
        all_results.extend(results)

    # Deduplicate
    unique = {r["id"]: r for r in all_results}

    return list(unique.values())