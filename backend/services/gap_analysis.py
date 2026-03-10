import json
import re
from backend.config.prompts import GAP_ANALYSIS_PROMPT
from backend.llm.mistral_client import call_llm
from backend.services.nist_retrieval import (
    fetch_similar_nist_records,
    format_nist_chunks_for_prompt
)

def extract_json(text: str):
    """Safely extract JSON from LLM output."""
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group())
    except json.JSONDecodeError:
        return None


def analyze_gap_for_domain(domain: str, text: str, use_semantic_search=True):
    """
    🔥 FAST GAP ANALYSIS — ONE CALL PER DOMAIN
    """

    # 🔽 Limit retrieval to keep speed high
    nist_records = fetch_similar_nist_records(
        policy_text=text,
        subdomain=domain,
        top_k=3
    )

    formatted_nist_chunks = format_nist_chunks_for_prompt(nist_records)

    prompt = GAP_ANALYSIS_PROMPT.format(
        domain=domain,
        subdomain=domain,
        organization_policy=text,
        nist_chunks=formatted_nist_chunks
    )

    response = call_llm(prompt)
    print(f"LLM response for domain '{domain}': {response}")

    result = extract_json(response)

    if not result:
        return {
            "domain": domain,
            "error": "Failed to parse LLM response",
            "raw_response": response
        }

    result["nist_records_used"] = [
        {
            "id": r.get("id"),
            "source": r.get("metadata", {}).get("source_file"),
            "similarity": r.get("similarity")
        }
        for r in nist_records
    ]

    print(f"✅ Gap analysis completed for domain: {domain}")

    return result
