import re

def preprocess_query(query: str) -> dict:
    """
    Clean and enrich user query before sending to RAG pipeline.
    Returns a dict with cleaned query and metadata flags.
    """

    # CLEAN & NORMALISE
    query = query.strip()
    query = re.sub(r'\s+', ' ', query)        # collapse multiple spaces
    query = re.sub(r'[^\w\s\?\.\,\!\-]', '', query)  # remove special chars

    # VALIDATE
    if not query:
        return {"error": "empty_query"}
    if len(query) > 500:
        query = query[:500]                    # hard limit for LLM safety

    # DETECT INTENT
    greetings = ["hi", "hello", "hey", "how are you", "good morning"]
    is_greeting = query.lower() in greetings

    # EXPAND / ENRICH  (add your domain acronyms here)
    acronym_map = {
        "ml":  "machine learning",
        "nlp": "natural language processing",
        "llm": "large language model",
        "rag": "retrieval augmented generation",
    }
    words = query.lower().split()
    expanded = [acronym_map.get(w, w) for w in words]
    clean_query = " ".join(expanded)

    return {
        "clean_query": clean_query,
        "original_query": query,
        "is_greeting": is_greeting,
        "is_empty": False,
        "char_count": len(clean_query),
    }


def clean_text(text: str) -> str:
    """
    Clean raw PDF text by removing noise and normalizing formatting.
    """
    # Fix hyphenated line breaks (e.g., "impor-\ntant" → "important")
    text = re.sub(r'-\n', '', text)

    # Replace newlines within paragraphs with a space
    text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)

    # Collapse multiple blank lines into one
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Remove page numbers (e.g., "Page 1", "- 2 -", standalone digits)
    text = re.sub(r'\bPage\s+\d+\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'^\s*[-–]?\s*\d+\s*[-–]?\s*$', '', text, flags=re.MULTILINE)

    # Remove excessive whitespace
    text = re.sub(r'[ \t]{2,}', ' ', text)

    # Strip leading/trailing whitespace
    text = text.strip()

    return text

def chunk_text(text: str, chunk_size: int = 400, overlap: int = 50) -> list[str]:
    """
    Split cleaned text into overlapping chunks by word count.
    - chunk_size: words per chunk (400 is safe for low-spec machines)
    - overlap: shared words between consecutive chunks (preserves context)
    """
    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk = ' '.join(words[start:end])

        if chunk.strip():  # Skip empty chunks
            chunks.append(chunk)

        start += chunk_size - overlap  # Slide window with overlap

    return chunks

SYNTHESIS_PHRASES = [
    "summarize", "summary", "main points", "key points",
    "main topics", "important topics", "conclusions",
    "what is this document about", "overview", "list"
]

def detect_query_intent(query: str) -> str:
    """
    Returns 'synthesis' for broad document queries,
    'specific' for targeted questions.
    """
    q = query.lower()
    if any(phrase in q for phrase in SYNTHESIS_PHRASES):
        return "synthesis"
    return "specific"