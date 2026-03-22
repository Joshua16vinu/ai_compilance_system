import json
import re
from backend.config.prompts import GAP_ANALYSIS_PROMPT
from backend.llm.mistral_client import call_llm
from backend.services.nist_retrieval import (
    fetch_similar_nist_records,
    format_nist_chunks_for_prompt,
     hybrid_fetch_nist_records,
    extract_relevant_text
)
from backend.config.prompts import GAP_ONLY_PROMPT, REVISED_POLICY_PROMPT 

def extract_json(text: str):
    """Safely extract JSON from LLM output."""
    if not text:
        return None

    try:
        # remove markdown json fences if present
        text = text.replace("```json", "").replace("```", "").strip()

        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            return None

        json_text = match.group()

        # attempt to fix truncated JSON
        open_braces = json_text.count("{")
        close_braces = json_text.count("}")

        if close_braces < open_braces:
            json_text += "}" * (open_braces - close_braces)

        return json.loads(json_text)

    except Exception as e:
        print("JSON extraction error:", e)
        return None


def analyze_gap_for_domain(domain: str, text: str, use_semantic_search=True):
    """
    FAST GAP ANALYSIS — ONE CALL PER DOMAIN
    """

    try:

        # Retrieve relevant NIST records
        # nist_records = fetch_similar_nist_records(
        #     policy_text=text,
        #     subdomain=domain,
        #     top_k=3
        # )
        nist_records = hybrid_fetch_nist_records(
    policy_text=text,
    domain=domain
)
        # formatted_nist_chunks = format_nist_chunks_for_prompt(nist_records)
        relevant_sentences = extract_relevant_text(nist_records, text)

        formatted_nist_chunks = "\n".join(relevant_sentences[:20])
        prompt = GAP_ANALYSIS_PROMPT.format(
            domain=domain,
            subdomain=domain,
            organization_policy=text,
            nist_chunks=formatted_nist_chunks
        )

        response = call_llm(prompt)

        print(f"\n===== LLM OUTPUT =====\n{response}\n======================")

        result = extract_json(response)

        if not result:
            print("⚠️ Failed to parse JSON from LLM response")

            return {
                "domain": domain,
                "subdomain": domain,
                "gap_analysis": [],
                "revised_policy": {
                    "introduction": "",
                    "statements": [],
                    "compliance_notes": ""
                },
                "implementation_roadmap": {
                    "short_term": [],
                    "mid_term": [],
                    "long_term": []
                },
                "nist_records_used": []
            }

        # Ensure required fields exist
        result.setdefault("domain", domain)
        result.setdefault("subdomain", domain)
        result.setdefault("gap_analysis", [])
        result.setdefault("revised_policy", {})
        result.setdefault("implementation_roadmap", {})

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

    except Exception as e:
        print("❌ Gap analysis error:", str(e))

        return {
            "domain": domain,
            "subdomain": domain,
            "gap_analysis": [],
            "revised_policy": {
                "introduction": "",
                "statements": [],
                "compliance_notes": ""
            },
            "implementation_roadmap": {
                "short_term": [],
                "mid_term": [],
                "long_term": []
            },
            "error": str(e),
            "nist_records_used": []
        }
    import json
 # add these imports


def analyze_gap_only(domain: str, text: str):
    """
    STEP 1 — Gap analysis only. No revised policy.
    Returns gap_analysis list + nist_records_used.
    """
    try:
        nist_records = fetch_similar_nist_records(
            policy_text=text,
            subdomain=domain,
            top_k=5
        )

        formatted_nist_chunks = format_nist_chunks_for_prompt(nist_records)
        print("chunks retrieved")
        prompt = GAP_ONLY_PROMPT.format(
            domain=domain,
            subdomain=domain,
            organization_policy=text,
            nist_chunks=formatted_nist_chunks
        )

        response = call_llm(prompt)
        print(f"\n===== GAP ONLY LLM OUTPUT =====\n{response}\n===============================")

        result = extract_json(response)

        if not result:
            print("⚠️ Failed to parse JSON from gap-only LLM response")
            return {
                "domain": domain,
                "subdomain": domain,
                "gap_analysis": [],
                "nist_records_used": []
            }

        result.setdefault("domain", domain)
        result.setdefault("subdomain", domain)
        result.setdefault("gap_analysis", [])

        result["nist_records_used"] = [
            {
                "id": r.get("id"),
                "source": r.get("metadata", {}).get("source_file"),
                "similarity": r.get("similarity")
            }
            for r in nist_records
        ]

        print(f"✅ Gap-only analysis completed for domain: {domain}")
        return result

    except Exception as e:
        print("❌ Gap-only analysis error:", str(e))
        return {
            "domain": domain,
            "subdomain": domain,
            "gap_analysis": [],
            "nist_records_used": [],
            "error": str(e)
        }


def generate_revised_policy(domain: str, text: str, gap_analysis: list):
    """
    STEP 2 — Revised policy generation using gap analysis output + original policy.
    """
    try:
        gap_analysis_str = json.dumps(gap_analysis, indent=2)

        prompt = REVISED_POLICY_PROMPT.format(
            domain=domain,
            subdomain=domain,
            organization_policy=text,
            gap_analysis=gap_analysis_str
        )

        response = call_llm(prompt)
        print(f"\n===== REVISED POLICY LLM OUTPUT =====\n{response}\n=====================================")

        result = extract_json(response)

        if not result:
            print("⚠️ Failed to parse JSON from revised policy LLM response")
            return {
                "domain": domain,
                "subdomain": domain,
                "revised_policy": {
                    "introduction": "",
                    "statements": [],
                    "compliance_notes": ""
                },
                "implementation_roadmap": {
                    "short_term": [],
                    "mid_term": [],
                    "long_term": []
                }
            }

        result.setdefault("domain", domain)
        result.setdefault("subdomain", domain)
        result.setdefault("revised_policy", {})
        result.setdefault("implementation_roadmap", {})

        print(f"✅ Revised policy generated for domain: {domain}")
        return result

    except Exception as e:
        print("❌ Revised policy generation error:", str(e))
        return {
            "domain": domain,
            "subdomain": domain,
            "revised_policy": {
                "introduction": "",
                "statements": [],
                "compliance_notes": ""
            },
            "implementation_roadmap": {
                "short_term": [],
                "mid_term": [],
                "long_term": []
            },
            "error": str(e)
        }