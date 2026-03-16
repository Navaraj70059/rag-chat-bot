from backend.services.chroma_service import upsert_documents
from backend.utils.text_utils import clean_text, chunk_text
from backend.utils.pdf_utils import generate_file_hash, save_temp_file, delete_file_if_exists,extract_text_from_pdf
from backend.config import CHUNK_SIZE, CHUNK_OVERLAP, MAX_PAGES

def ingest_document(file_content: bytes, filename: str) -> dict:
    """
    Core ingestion logic. Used by both the upload route and ingest.py.
    Takes raw file bytes, processes and stores in ChromaDB.
    """
    file_hash = generate_file_hash(file_content)
    temp_path = save_temp_file(file_content)

    try:
        raw_pages = extract_text_from_pdf(temp_path)

        if len(raw_pages) > MAX_PAGES:
            raise ValueError(f"PDF has {len(raw_pages)} pages. Maximum allowed is {MAX_PAGES}.")

        cleaned_text = " ".join([clean_text(page) for page in raw_pages])
        text_chunks  = chunk_text(cleaned_text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP)
        upsert_documents(text_chunks, file_hash, filename)

    finally:
        delete_file_if_exists(temp_path)

    return {
        "chunks": len(text_chunks),
        "file_hash": file_hash,
        "filename": filename
    }