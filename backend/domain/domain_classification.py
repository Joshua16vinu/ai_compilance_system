# DOMAIN_KB = {
#     "ISMS": [
#         "information security management system policies audit compliance controls",
#         "ISO 27001 governance security controls audit documentation risk governance",
#         "organizational security policies procedures asset management access control"
#     ],

#     "Risk Management": [
#         "risk assessment mitigation threats vulnerabilities likelihood impact",
#         "risk analysis risk treatment enterprise risk management residual risk",
#         "threat modeling vulnerability identification control effectiveness risk register"
#     ],

#     "Patch Management": [
#         "software patching updates vulnerability fixes system updates",
#         "patch deployment patch testing CVE fixes update management system hardening",
#         "operating system updates application updates patch lifecycle management"
#     ],

#     "Data Privacy & Security": [
#         "data protection privacy encryption personal data security controls",
#         "GDPR compliance data confidentiality integrity access control PII protection",
#         "data classification retention masking breach prevention privacy controls"
#     ]
# }


DOMAIN_KB = {

    # ----------------------------------------------------------
    # 1. ISMS / GOVERNANCE
    #    ISO 27001 Clauses 4-10 | NIST CSF: Govern (GV)
    #    SP 800-53: PM, PL families
    # ----------------------------------------------------------
    "ISMS": [
        "information security management system ISMS governance framework policy",
        "ISO 27001 security policy statement scope objectives management review",
        "organizational security governance audit compliance controls documentation",
        "information security roles responsibilities accountability senior leadership",
        "ISMS scope continual improvement corrective action nonconformity",
        "security policy approval communication review update periodic",
        "statement of applicability SoA risk treatment plan ISMS controls",
        "cybersecurity strategy enterprise risk tolerance organizational context",
        "NIST CSF govern function policy oversight cybersecurity program",
        "security committee steering group CISO board reporting governance",
    ],

    # ----------------------------------------------------------
    # 2. RISK MANAGEMENT
    #    NIST SP 800-30 Rev.1 | ISO 27001 Clause 6 | CSF: Identify (ID.RA)
    #    SP 800-53: RA family
    # ----------------------------------------------------------
    "Risk Management": [
        "risk assessment identification evaluation treatment mitigation likelihood impact",
        "risk register residual risk appetite tolerance acceptance transfer avoidance",
        "threat modeling vulnerability identification threat intelligence risk analysis",
        "enterprise risk management ERM inherent risk control effectiveness",
        "risk treatment plan risk owner risk review periodic reassessment",
        "qualitative quantitative risk scoring heat map risk matrix",
        "business impact analysis BIA critical asset risk prioritization",
        "supply chain risk third party vendor risk assessment outsourcing",
        "NIST SP 800-30 risk assessment guide RA-3 RA-5 risk monitoring",
        "cyber risk appetite statement risk tolerance organizational risk posture",
    ],

    # ----------------------------------------------------------
    # 3. ACCESS CONTROL
    #    NIST SP 800-53: AC family | ISO 27001: A.5.15-A.5.18, A.8.2-A.8.6
    #    CSF: Protect (PR.AA)
    # ----------------------------------------------------------
    "Access Control": [
        "access control user access management role based access control RBAC",
        "least privilege need to know access rights provisioning deprovisioning",
        "authentication MFA multi factor authentication password policy SSO",
        "authorization permissions access review recertification entitlements",
        "privileged access management PAM admin accounts elevated rights",
        "identity access management IAM user lifecycle joiner mover leaver",
        "session management timeout logout inactivity lock screen",
        "remote access VPN zero trust network access ZTNA",
        "single sign on federated identity SAML OAuth directory services AD LDAP",
        "access control list ACL firewall rules network segmentation VLAN",
    ],

    # ----------------------------------------------------------
    # 4. DATA PROTECTION & PRIVACY
    #    ISO 27001: A.5.33, A.8.11-A.8.12 | GDPR | NIST SP 800-188
    #    SP 800-53: SI, MP families | CSF: Protect (PR.DS)
    # ----------------------------------------------------------
    "Data Privacy & Security": [
        "data protection privacy personal data PII sensitive information handling",
        "data classification public internal confidential restricted secret",
        "GDPR data subject rights lawful basis processing privacy notice consent",
        "data retention deletion disposal secure erasure media sanitization",
        "encryption at rest in transit TLS SSL AES key management PKI",
        "data masking tokenization anonymization pseudonymization",
        "data loss prevention DLP exfiltration prevention data leakage",
        "privacy by design data minimization purpose limitation storage limitation",
        "cross border data transfer adequacy decision standard contractual clauses",
        "PII inventory data mapping data flow diagram DPIA privacy impact assessment",
    ]
}
# DOMAIN_KEYWORDS = {
#     "ISMS": ["policy", "audit", "compliance", "control", "governance"],
#     "Risk Management": ["risk", "threat", "vulnerability", "impact", "likelihood"],
#     "Patch Management": ["patch", "update", "fix", "vulnerability", "upgrade"],
#     "Data Privacy & Security": ["data", "privacy", "encryption", "pii", "confidential"]
# }

DOMAIN_KEYWORDS = {
    "ISMS": [
        "policy", "governance", "audit", "compliance", "isms",
        "framework", "control", "iso 27001", "management system",
        "scope", "review", "documentation", "oversight", "program",
    ],
    "Risk Management": [
        "risk", "threat", "vulnerability", "likelihood", "impact",
        "residual", "mitigation", "treatment", "register", "appetite",
        "tolerance", "assessment", "analyze", "hazard", "exposure",
    ],
    "Access Control": [
        "access", "authentication", "authorization", "permission",
        "rbac", "privilege", "identity", "role", "entitlement",
        "password", "mfa", "session", "login", "credential",
    ],
    "Data Privacy & Security": [
        "data", "privacy", "pii", "personal", "confidential",
        "gdpr", "encryption", "classification", "retention", "masking",
        "breach", "consent", "processing", "sensitive", "disclosure",
    ]
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