"""
app.py
──────
Main FastAPI entry point.
This file only does 3 things:
1. Creates the FastAPI app
2. Adds middleware (CORS)
3. Registers routes

All business logic lives in services/ and routes/.
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes.chat import router
from backend.config import HOST, PORT

app = FastAPI(
    title="RAG Chatbot API",
    description="Chat with your PDF documents using a local LLaMA model",
    version="1.0.0"
)

# ── CORS Middleware ──
# Allows the frontend (HTML/JS) to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # In production, replace * with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register Routes ──
app.include_router(router)


# ── Health Check ──
@app.get("/")
def health_check():
    return {"status": "running", "message": "RAG Chatbot API is live!"}


# ── Run the server ──
if __name__ == "__main__":
    uvicorn.run("backend.app:app", host=HOST, port=PORT, reload=True)
