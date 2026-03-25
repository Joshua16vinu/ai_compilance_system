from PyPDF2 import PdfReader
from backend.ocr.ocr_engine import ocr_pdf


import pdfplumber

def extract_text_from_pdf(pdf_path: str) -> str:
    text = ""

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"

    return text

# def extract_text_from_pdf(pdf_path: str) -> str:
#     """
#     Tries normal PDF text extraction.
#     Falls back to OCR if text is empty.
#     """
#     reader = PdfReader(pdf_path)
#     text = ""

#     for page in reader.pages:
#         extracted = page.extract_text()
#         if extracted:
#             text += extracted + "\n"

#     # If text is too small, assume scanned PDF
#     if len(text.strip()) < 200:
#         print("⚠️ Low text detected, switching to OCR...")
#         text = ocr_pdf(pdf_path)

#     return text
