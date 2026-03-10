import json
from flask import Blueprint, request, Response
from backend.services.gap_analysis import analyze_gap_for_domain

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
