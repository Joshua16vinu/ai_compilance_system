DOMAIN_KB = {
    "ISMS": [
        "information security management system policies audit compliance controls",
        "ISO 27001 governance security controls audit documentation risk governance",
        "organizational security policies procedures asset management access control"
    ],

    "Risk Management": [
        "risk assessment mitigation threats vulnerabilities likelihood impact",
        "risk analysis risk treatment enterprise risk management residual risk",
        "threat modeling vulnerability identification control effectiveness risk register"
    ],

    "Patch Management": [
        "software patching updates vulnerability fixes system updates",
        "patch deployment patch testing CVE fixes update management system hardening",
        "operating system updates application updates patch lifecycle management"
    ],

    "Data Privacy & Security": [
        "data protection privacy encryption personal data security controls",
        "GDPR compliance data confidentiality integrity access control PII protection",
        "data classification retention masking breach prevention privacy controls"
    ]
}

DOMAIN_KEYWORDS = {
    "ISMS": ["policy", "audit", "compliance", "control", "governance"],
    "Risk Management": ["risk", "threat", "vulnerability", "impact", "likelihood"],
    "Patch Management": ["patch", "update", "fix", "vulnerability", "upgrade"],
    "Data Privacy & Security": ["data", "privacy", "encryption", "pii", "confidential"]
}

import numpy as np

_domain_embeddings_cache = None

def load_domain_embeddings(embedder):
    global _domain_embeddings_cache

    if _domain_embeddings_cache is None:
        _domain_embeddings_cache = {}

        for domain, descriptions in DOMAIN_KB.items():
            _domain_embeddings_cache[domain] = [
                embedder.encode(desc, normalize_embeddings=True)
                for desc in descriptions
            ]

    return _domain_embeddings_cache

def keyword_score(chunk, keywords):
    chunk_lower = chunk.lower()
    count = sum(1 for k in keywords if k in chunk_lower)
    return count / (len(keywords) + 1e-5)


def classify_chunk_domains(chunk, embedder, threshold=0.06):

    domain_embeds = load_domain_embeddings(embedder)
    chunk_embedding = embedder.encode(chunk, normalize_embeddings=True)

    scores = {}

    for domain, embed_list in domain_embeds.items():

        # 🔹 Semantic score = max similarity across descriptions
        semantic_scores = [
            float(np.dot(chunk_embedding, emb))
            for emb in embed_list
        ]
        semantic_score = max(semantic_scores)

        # 🔹 Keyword score
        kw_score = keyword_score(chunk, DOMAIN_KEYWORDS[domain])

        # 🔹 Hybrid score (weighted)
        final_score = 0.85 * semantic_score + 0.15 * kw_score

        scores[domain] = final_score

    # 🔹 Sort domains
    sorted_domains = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    top1, top2 = sorted_domains[0], sorted_domains[1]

    # 🔹 Stable multi-domain logic
    if (top1[1] - top2[1]) < threshold:
        selected = [top1[0], top2[0]]
    else:
        selected = [top1[0]]

    return {
        "domains": selected,
        "scores": scores,
        "top_scores": {
            "top1": top1,
            "top2": top2
        }
    }