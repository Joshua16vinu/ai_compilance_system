import json
import re
import os
from backend.config.prompts import DOMAIN_CHUNKING_PROMPT
from backend.llm.mistral_client import call_llm


def extract_json(text: str):
    """Extract JSON object from LLM output safely."""

    # 1️⃣ Remove markdown code fences
    text = re.sub(r"```json", "", text)
    text = re.sub(r"```", "", text)

    # 2️⃣ Extract JSON block
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None

    json_str = match.group().strip()

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        print("JSON parsing error:", e)
        print("Problematic JSON:", json_str[:500])
        return None


def chunk_by_domain(policy_text: str) -> list:
    """
    Chunk policy text by domain.

    Returns a LIST of objects in this format:
    {
      "domain": "ISMS",
      "text": "...",
      "subdomains": [...]
    }
    """
    print("Starting domain chunking...")
    prompt = DOMAIN_CHUNKING_PROMPT.format(policy_text=policy_text)
    response = call_llm(prompt)

    # 1️⃣ KEEP RAW OUTPUT (audit/debug)
    os.makedirs("logs", exist_ok=True)
    with open("logs/domain_chunking_raw.log", "a", encoding="utf-8") as f:
        f.write("\n==== RAW LLM OUTPUT ====\n")
        f.write(response)
        f.write("\n=======================\n")

    # 2️⃣ PARSE JSON
    data = extract_json(response)
    if not data:
        return []

    # 3️⃣ NORMALIZE TO REQUIRED FORMAT
    normalized_output = []

    for domain, obj in data.items():
        if not obj:
            continue

        # Expecting:
        # {
        #   "text": [...],
        #   "subdomains": [...]
        # }

        text_items = obj.get("text", [])
        subdomains = obj.get("subdomains", [])

        combined_text = " ".join(
            t.strip() for t in text_items if isinstance(t, str) and t.strip()
        )

        if not combined_text:
            continue

        normalized_output.append({
            "domain": domain,
            "text": combined_text,
            "subdomains": subdomains
        })

    return normalized_output
