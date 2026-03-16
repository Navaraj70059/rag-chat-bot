"""
chat.py
───────
API routes for the RAG chatbot.
Handles:
- POST /upload  → receives a PDF, processes it, stores in ChromaDB
- POST /ask     → receives a question, returns an AI answer
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from backend.config import MAX_UPLOAD_MB
from backend.services.rag_service import get_rag_answer
from backend.services.ingest_service import ingest_document

router = APIRouter()


class ChatQuery(BaseModel):
    query: str

ALLOWED_TYPE = "application/pdf"
MAX_BYTES    = MAX_UPLOAD_MB * 1024 * 1024

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload a PDF, extract its text, and store it in ChromaDB.
    Re-uploading the same file is safe — it won't create duplicates.
    """
    # Validate content type
    if file.content_type != ALLOWED_TYPE:
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    file_content = await file.read()

    # Validate size
    if len(file_content) > MAX_BYTES:
        raise HTTPException(status_code=413, detail=f"File too large. Max {MAX_UPLOAD_MB}MB.")

    # Validate magic bytes
    if not file_content.startswith(b"%PDF"):
        raise HTTPException(status_code=400, detail="Invalid PDF file.")

    try:
        result = ingest_document(file_content, file.filename) # type: ignore
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "message": f"Successfully indexed {result['chunks']} chunks.",
        "file_id": result["file_hash"]
    }

@router.post("/ask")
async def ask_question(chat: ChatQuery, session_id: str = "default_user"):
    """
    Receive a question and return an AI answer based on uploaded documents.
    Uses session_id to maintain separate chat histories per user.
    """
    answer = get_rag_answer(chat.query, session_id)
    return {"answer": answer}
