from backend.ocr.pdf_loader import extract_text_from_pdf
from backend.ocr.text_cleaner import clean_text
from backend.chunking.domain_chunker import chunk_by_domain

def process_pdf(pdf_path: str):
    """
    Complete PDF → OCR → Clean → Domain Chunk pipeline
    """
    raw_text = extract_text_from_pdf(pdf_path)

    if not raw_text.strip():
        raise ValueError("No text extracted from PDF")

    cleaned_text = clean_text(raw_text)
    chunks = chunk_by_domain(cleaned_text)
    print(f"Extracted {len(chunks)} domain-specific chunks from PDF")
    print("pdf pipeline completed")
    return chunks
