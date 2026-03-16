"""
chroma_service.py
─────────────────
Handles all ChromaDB operations:
- Connecting to the database
- Storing document chunks
- Querying for relevant chunks
"""

import chromadb
from backend.config import CHROMA_DB_PATH, COLLECTION_NAME
from backend.config import DISTANCE_THRESHOLD

# Connect to ChromaDB once when the app starts
chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)


def get_document_count() -> int:
    """
    Returns how many document chunks are stored in ChromaDB.
    Used to check if any PDFs have been uploaded before answering.
    """
    return collection.count()


def upsert_documents(text_chunks: list[str], file_hash: str, filename: str) -> None:
    """
    Save document chunks into ChromaDB.
    Uses upsert so re-uploading the same file won't create duplicates.

    Args:
        text_chunks: List of text strings (one per page)
        file_hash: Unique fingerprint of the file (used as ID prefix)
        filename: Original filename (stored as metadata)
    """
    collection.upsert(
        documents=text_chunks,
        ids=[f"{file_hash}_p{i}" for i in range(len(text_chunks))],
        metadatas=[{"source": filename, "page": i} for i in range(len(text_chunks))]
    )


def query_documents(query: str, n_results: int = 3) -> list:
    """
        Search ChromaDB for the most relevant document chunks.

        Args:
            query: The user's question
            n_results: How many chunks to retrieve

        Returns:
            ChromaDB results dict with documents and distances
        """
    results = collection.query(
        query_texts=[query],
        n_results=n_results,
        include=["documents", "distances"]
    )

    docs = results["documents"][0] # type: ignore
    distances = results["distances"][0] # type: ignore

    filtered = [
        doc for doc, dist in zip(docs, distances)
        if dist <= DISTANCE_THRESHOLD        # use the constant
    ]

    return filtered if filtered else []      # return empty list, not a fake string