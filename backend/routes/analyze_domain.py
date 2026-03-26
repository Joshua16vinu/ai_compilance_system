import json
from flask import Blueprint, request, Response
from backend.services.gap_analysis import analyze_gap_for_domain, generate_revised_policy, analyze_gap_only
from backend.services.gap_analysis import generate_roadmap_stream , generate_revised_policy_stream
from concurrent.futures import ThreadPoolExecutor, as_completed
analyze_bp = Blueprint("analyze", __name__)

@analyze_bp.route("/analyze-domain", methods=["POST"])
def analyze_domain():
    """
    Perform GAP ANALYSIS for ONE DOMAIN.

    Expected JSON:
    {
      "domain": "ISMS",
      "text": "domain policy text..."
    }
    """

    data = request.get_json()
    print("Incoming payload:", data)

    domain = data.get("domain")
    text = data.get("text")

    if "subdomains" in data:
        print("Ignoring subdomains for domain-level analysis")

    if not domain or not text:
        return Response("Invalid request payload", status=400)

    try:
        result = analyze_gap_for_domain(
            domain=domain,
            text=text,
            use_semantic_search=True
        )
    except Exception as e:
        return Response(
            f"ERROR: Gap analysis failed\n{str(e)}",
            mimetype="text/plain",
            status=500
        )

    return Response(
        json.dumps(result, indent=2),
        mimetype="application/json",
        status=200
    )


@analyze_bp.route("/analyze-gap", methods=["POST"])
def analyze_gap():
    """
    STEP 1 — Gap Analysis only.

    Expected JSON:
    {
      "domain": "ISMS",
      "text": "organization policy text..."
    }

    Returns gap_analysis list + nist_records_used.
    """
    data = request.get_json()
    print("Incoming payload:", data)

    domain = data.get("domain")
    text = data.get("text")

    if not domain or not text:
        return Response("Invalid request payload", status=400)

    try:
        result = analyze_gap_for_domain(domain=domain, text=text)
    except Exception as e:
        return Response(
            f"ERROR: Gap analysis failed\n{str(e)}",
            mimetype="text/plain",
            status=500
        )

    return Response(
        json.dumps(result, indent=2),
        mimetype="application/json",
        status=200
    )


# @analyze_bp.route("/revised-policy", methods=["POST"])
# def revised_policy():
#     """
#     STEP 2 — Revised Policy generation.

#     Expected JSON:
#     {
#       "domain": "ISMS",
#       "text": "original organization policy text...",
#       "gap_analysis": [ ...gap objects from /analyze-gap response... ]
#     }

#     Returns revised_policy + implementation_roadmap.
#     """
#     data = request.get_json()
#     print("Incoming payload:", data)

#     domain = data.get("domain")
#     text = data.get("text")
#     gap_analysis = data.get("gap_analysis", [])

#     if not domain or not text:
#         return Response("Invalid request payload", status=400)

#     if not isinstance(gap_analysis, list):
#         return Response("'gap_analysis' must be a list", status=400)

#     try:
#         result = generate_revised_policy(
#             domain=domain,
#             text=text,
#             gap_analysis=gap_analysis
#         )
#     except Exception as e:
#         return Response(
#             f"ERROR: Revised policy generation failed\n{str(e)}",
#             mimetype="text/plain",
#             status=500
#         )

#     return Response(
#         json.dumps(result, indent=2),
#         mimetype="application/json",
#         status=200
#     )

@analyze_bp.route("/revised-policy", methods=["POST"])
def revised_policy():
    data = request.get_json()

    text = data.get("text")
    print("Original policy text:", text)
    gap_analysis = data.get("gap_analysis")
    print("Gap analysis input:", gap_analysis)


    # ✅ Validate input
    if not text or not gap_analysis:
        return Response("Missing 'text' or 'gap_analysis'", status=400)

    if not isinstance(gap_analysis, str):
        return Response("'gap_analysis' must be a string", status=400)

    def generate():
        try:
            stream = generate_revised_policy_stream(text, gap_analysis)

            for chunk in stream:
                print(chunk, end="", flush=True)
                yield chunk.encode("utf-8")   # ✅ FIX

            

        except Exception as e:
            yield f"\nERROR: {str(e)}".encode("utf-8")   # ✅ FIX

    return Response(
        generate(),
        mimetype="text/plain",
        direct_passthrough=True   # ⚡ helps streaming
    )

@analyze_bp.route("/implementation-roadmap", methods=["POST"])
def implementation_roadmap():
    data = request.get_json()

    text = data.get("text")
    revised_policy = data.get("revised_policy")

    # ✅ Validation
    if not text or not revised_policy:
        return Response("Missing 'text' or 'revised_policy'", status=400)

    def generate():
        try:
            stream = generate_roadmap_stream(text, revised_policy)

            for chunk in stream:
                print(chunk, end="", flush=True)   # 👈 debug
                yield chunk.encode("utf-8")        # 👈 streaming fix

        except Exception as e:
            yield f"\nERROR: {str(e)}".encode("utf-8")

    return Response(
        generate(),
        mimetype="text/plain",
        direct_passthrough=True
    )
@analyze_bp.route("/analyze-gap-batch", methods=["POST"])
def analyze_gap_batch():
    data = request.get_json()

    categorized = data.get("categorized_policy")

    if not categorized or not isinstance(categorized, dict):
        return Response("Missing or invalid 'categorized_policy'", status=400)

    def generate():
        try:
            with ThreadPoolExecutor(max_workers=2) as executor:
                futures = {
                    executor.submit(analyze_gap_only, domain, domain_text): domain
                    for domain, domain_text in categorized.items()
                    if domain_text.strip()
                }

                for future in as_completed(futures):
                    result = future.result()

                    chunk = json.dumps(result) + "\n"

                    print(f"\n✅ GAP DONE: {result['domain']}")
                    yield chunk.encode("utf-8")

        except Exception as e:
            yield f"\nERROR: {str(e)}".encode("utf-8")

    return Response(
        generate(),
        mimetype="text/plain",
        direct_passthrough=True
    )