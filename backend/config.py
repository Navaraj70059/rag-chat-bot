"""
config.py
─────────
Central configuration for the RAG Chatbot.

All tuneable settings live in .env — see .env.example for reference.
This file only reads them and derives dependent values.
Nothing is hardcoded here except safe defaults for low-end hardware.
"""

import os
from dotenv import load_dotenv

load_dotenv()


# ─────────────────────────────────────────────
# LLM — Model Loading
# Controls how LLaMA is loaded into memory.
# Adjust these in .env based on your hardware.
# ─────────────────────────────────────────────

# Path to the local .gguf model file
MODEL_PATH = os.getenv("MODEL_PATH", "models/llama-model.gguf")

# Maximum tokens the model can hold in one pass (prompt + answer combined)
# Low-end laptop: 2560 | Mid-range: 4096 | GPU machine: 8192
N_CTX = int(os.getenv("N_CTX", 2560))

# Number of CPU threads for inference — set to your CPU thread count
N_THREADS = int(os.getenv("N_THREADS", 4))

# Tokens processed in parallel — higher is faster but uses more RAM
N_BATCH = int(os.getenv("N_BATCH", 512))

# Number of model layers offloaded to GPU
# 0 = CPU only | 1 = Mac Metal | 35+ = NVIDIA GPU
N_GPU_LAYERS = int(os.getenv("N_GPU_LAYERS", 0))


# ─────────────────────────────────────────────
# LLM — Answer Generation
# Controls how many tokens the model generates.
# Synthesis queries (summaries) get more tokens
# than specific factual questions.
# ─────────────────────────────────────────────

# Max tokens for short factual answers ("What is X?")
MAX_TOKENS_SPECIFIC = int(os.getenv("MAX_TOKENS_SPECIFIC", 300))

# Max tokens for broad synthesis answers ("Summarize", "List topics")
MAX_TOKENS_SYNTHESIS = int(os.getenv("MAX_TOKENS_SYNTHESIS", 500))


# ─────────────────────────────────────────────
# ChromaDB — Vector Store
# Where embeddings and document chunks are saved.
# ─────────────────────────────────────────────

# Folder where ChromaDB persists its data
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")

# Name of the collection storing PDF chunks
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "pdf_docs")

# How many top chunks to retrieve per query
MAX_CHUNKS = int(os.getenv("MAX_CHUNKS", 3))

# Relevance cutoff — chunks with distance above this are considered irrelevant
# Lower = stricter. Tune by running debug_distances() on your own documents.
DISTANCE_THRESHOLD = float(os.getenv("DISTANCE_THRESHOLD", 1.6))


# ─────────────────────────────────────────────
# Chat History
# Controls how much conversation context is
# kept and sent back to the model each turn.
# ─────────────────────────────────────────────

# Number of previous exchanges included in each prompt
# 1 exchange = 1 user message + 1 assistant reply
HISTORY_WINDOW = int(os.getenv("HISTORY_WINDOW", 5))


# ─────────────────────────────────────────────
# Prompt Budget
# Derived automatically from N_CTX so the prompt
# never exceeds the model's context window.
# Change N_CTX in .env — these adjust automatically.
# ─────────────────────────────────────────────

# Rough characters-per-token estimate for English text
CHARS_PER_TOKEN = 3

# Reserved tokens for the system role + prompt labels (### Context: etc.)
SYSTEM_PROMPT_TOKENS = 50

# Tokens left after reserving space for the answer and system prompt
AVAILABLE_TOKENS = N_CTX - MAX_TOKENS_SPECIFIC - SYSTEM_PROMPT_TOKENS

# Convert to characters for easier slicing in Python
AVAILABLE_CHARS = AVAILABLE_TOKENS * CHARS_PER_TOKEN

# Budget split across the three variable sections of the prompt
# 60% → document context  (most important — drives answer quality)
# 25% → conversation history
# 15% → user query
DOC_CHAR_LIMIT     = int(AVAILABLE_CHARS * 0.60)
HISTORY_CHAR_LIMIT = int(AVAILABLE_CHARS * 0.25)
QUERY_CHAR_LIMIT   = int(AVAILABLE_CHARS * 0.15)


# ─────────────────────────────────────────────
# PDF Upload & Ingestion
# Controls what files are accepted and how they
# are split into chunks for ChromaDB storage.
# ─────────────────────────────────────────────

# Maximum allowed PDF file size in megabytes
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", 20))

# PDFs exceeding this page count are rejected at upload
MAX_PAGES = int(os.getenv("MAX_PAGES", 50))

# Characters per chunk when splitting extracted text
# Smaller = more precise retrieval | Larger = more context per chunk
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 500))

# Overlap between consecutive chunks so context is not lost at boundaries
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 50))


# ─────────────────────────────────────────────
# Server
# ─────────────────────────────────────────────

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))


# ─────────────────────────────────────────────
# Prompt — System Role
# Injected at the top of every prompt to keep
# the model focused on the uploaded documents.
# Short and specific beats long and generic.
# ─────────────────────────────────────────────

SYSTEM_ROLE = "You are a document analyst. Only answer from the provided context."