# 🤖 RAG Chatbot — PDF Intelligence

Chat with your PDF documents using a **local LLaMA model** — no API keys, no cloud, 100% private.

Built with FastAPI · ChromaDB · llama-cpp-python · Vanilla JS

---

## 🚀 Quick Start

### 1. Clone the project
```bash
git clone https://github.com/yourusername/rag-chatbot.git
cd rag-chatbot
```

### 2. Create & activate virtual environment
```bash
python -m venv venv

# Windows (Git Bash)
source venv/Scripts/activate

# Mac / Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
```bash
# Copy the example file
cp .env.example .env

# Edit .env and set your model path
MODEL_PATH=models/your-model-name.gguf
```

### 5. Add your LLaMA model
Place your `.gguf` model file inside the `models/` folder.
> ⚠️ The `models/` folder is in `.gitignore` — model files are too large for GitHub.

### 6. Run the backend
```bash
python -m backend.app
```
Backend will start at: `http://127.0.0.1:8000`

### 7. Open the frontend
Open `frontend/index.html` in your browser.

---

## 📁 Project Structure

```
rag-chatbot/
├── .env                      
├── .env.example              # Template 
├── .gitignore
├── requirements.txt
├── README.md
│
├── backend/
│   ├── app.py                # FastAPI entry point
│   ├── config.py             # Reads settings from .env
│   ├── routes/
│   │   └── chat.py           # /upload and /ask endpoints
│   ├── services/
│   │   ├── rag_service.py    # RAG pipeline logic
│   │   ├── llama_service.py  # LLaMA model inference
│   │   └── chroma_service.py # ChromaDB operations
│   └── utils/
│       └── helpers.py        # PDF extraction, hashing, etc.
│
├── frontend/
│   ├── index.html
│   ├── css/style.css
│   └── js/main.js
│
├── scripts/
│   └── ingest.py             # Bulk load PDFs into ChromaDB
│
├── data/documents/           # Put PDFs here for bulk ingestion
├── models/                   # Put your .gguf model here
└── chroma_db/                # Auto-generated — don't touch
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET  | `/`         | Health check |
| POST | `/upload`   | Upload & index a PDF |
| POST | `/ask`      | Ask a question |

---

## ⚙️ Hardware Requirements

This project is tuned for a mid-range CPU laptop:
- RAM: 8GB minimum
- CPU: Any modern i3/i5/Ryzen
- GPU: Not required (runs on CPU)

## Hardware configuration

Copy `.env.example` to `.env` and set these based on your machine:

| Setting       | Low-end laptop (8GB) | Mid-range (16GB) | Mac M1/M2 | GPU machine |
|---------------|---------------------|------------------|-----------|-------------|
| N_CTX         | 2560                | 4096             | 4096      | 8192        |
| N_THREADS     | 4                   | 8                | 8         | 8           |
| N_GPU_LAYERS  | 0                   | 0                | 1         | 35          |
| MAX_NEW_TOKENS| 300                 | 512              | 512       | 1024        |

Everything else (doc limits, history limits, prompt budget) 
calculates automatically from these four values.
---

## 📦 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI + Python |
| AI Model | LLaMA (local .gguf via llama-cpp-python) |
| Vector DB | ChromaDB |
| PDF Parsing | pypdf |
| Frontend | HTML + CSS + jQuery |
