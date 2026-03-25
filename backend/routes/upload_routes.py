import os
import json
from flask import Blueprint, request, current_app, Response
from backend.utils.file_utils import allowed_file
from backend.services.pdf_pipeline import process_pdf
import traceback
upload_bp = Blueprint("upload", __name__)

@upload_bp.route("/upload-pdf", methods=["POST"])
def upload_pdf():
    """
    Upload PDF and return DOMAIN CHUNKS immediately.
    Gap analysis is triggered separately per domain.
    """

    if "file" not in request.files:
        return Response("ERROR: No file part", status=400)

    file = request.files["file"]

    if file.filename == "":
        return Response("ERROR: No selected file", status=400)

    if not allowed_file(file.filename):
        return Response("ERROR: Only PDF files are allowed", status=400)

    upload_folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_folder, exist_ok=True)

    file_path = os.path.join(upload_folder, file.filename)
    file.save(file_path)

    try:
        domain_chunks = process_pdf(file_path)
    except Exception as e:
        return Response(
            
           
            f"ERROR: PDF processing failed\n{str(e)}",
            mimetype="text/plain",
            status=500
        )

    # 🔥 RETURN FAST — NO GAP ANALYSIS HERE
    return Response(
        json.dumps(domain_chunks, indent=2),
        mimetype="application/json",
        status=200
    )
