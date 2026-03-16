"""
ingest.py
─────────
Bulk document ingestion script.
Use this to load all PDFs from data/documents/ into ChromaDB
without needing to upload them one by one through the UI.

Usage:
    python scripts/ingest.py
"""

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.ingest_service import ingest_document

DOCUMENTS_FOLDER = "data/documents"

def ingest_all_documents():
    pdf_files = [f for f in os.listdir(DOCUMENTS_FOLDER) if f.endswith(".pdf")]

    if not pdf_files:
        print("No PDF files found in data/documents/")
        return

    print(f"Found {len(pdf_files)} PDF(s) to ingest...\n")

    for filename in pdf_files:
        filepath = os.path.join(DOCUMENTS_FOLDER, filename)

        with open(filepath, "rb") as f:
            file_content = f.read()

        try:
            result = ingest_document(file_content, filename)
            print(f"  Done: {filename} — {result['chunks']} chunks indexed")
        except ValueError as e:
            print(f"  Skipped: {filename} — {e}")

    print("\nAll documents ingested.")

if __name__ == "__main__":
    ingest_all_documents()
# ```

# ---

# ## How pdf flow works end to end
# ```
# First time setup (before app starts):
#   1. Put PDFs in data/documents/
#   2. Run: python scripts/ingest.py
#   3. ChromaDB is now populated

# App running (user uploads new PDF):
#   1. User drags PDF into UI
#   2. POST /upload fires
#   3. Same ingest_document() runs
#   4. ChromaDB updated instantly