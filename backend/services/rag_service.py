"""
rag_service.py
──────────────
Core RAG (Retrieval-Augmented Generation) logic.
This is the brain of the chatbot:
1. Retrieves relevant chunks from ChromaDB
2. Builds a prompt with context + chat history
3. Sends it to LLaMA for an answer
"""

from collections import defaultdict
from backend.services.chroma_service import query_documents, get_document_count
from backend.services.llama_service import generate_answer
from backend.utils.text_utils import preprocess_query, detect_query_intent
from backend.config import DOC_CHAR_LIMIT, HISTORY_CHAR_LIMIT, MAX_TOKENS_SPECIFIC, MAX_TOKENS_SYNTHESIS, QUERY_CHAR_LIMIT,HISTORY_WINDOW, MAX_CHUNKS, SYSTEM_ROLE

# In-memory chat history storage
# Structure: { "session_id": [ {"role": "User", "content": "..."}, ... ] }
chat_history: dict = defaultdict(list)




def get_rag_answer(raw_query: str, session_id: str = "default_user") -> str:
    """
    Full RAG pipeline: retrieve → build prompt → generate → save history.

    Args:
        query: The user's question
        session_id: Identifies the conversation (for multi-user support)

    Returns:
        The AI's answer as a string
    """
    # Check if any documents have been uploaded yet
    if get_document_count() == 0:
        return "⚠️ No documents uploaded yet! Please upload a PDF first using the sidebar on the left, then ask your question."


     # --- PRE-PROCESSING user query---
    processed = preprocess_query(raw_query)
    if processed.get("error"):
        return "Please enter a valid question."
    if processed["is_greeting"]:
        return "Hello! Ask me anything about the uploaded documents."

    clean_query = processed["clean_query"]
    intent      = detect_query_intent(clean_query)

    history         = chat_history[session_id][-HISTORY_WINDOW:]
    history_context = _format_history(history)

    # Synthesis needs more chunks — specific needs fewer but more precise
    if intent == "synthesis":
        docs = query_documents(clean_query, n_results=6)
    else:
        docs = query_documents(clean_query, n_results=3)

    if not docs:
        return "I don't have that information in the uploaded documents."

    doc_context = "\n\n---\n\n".join(docs[:6 if intent == "synthesis" else MAX_CHUNKS])
    prompt      = _build_prompt(doc_context, history_context, clean_query, intent)

    max_tokens = MAX_TOKENS_SYNTHESIS if intent == "synthesis" else MAX_TOKENS_SPECIFIC
    answer     = generate_answer(prompt, max_tokens=max_tokens)
    # answer = generate_answer(prompt)

    chat_history[session_id].append({"role": "User",      "content": clean_query})
    chat_history[session_id].append({"role": "Assistant", "content": answer})

    return answer


# budget-aware, structured
def _format_history(history: list, max_chars: int = 1500) -> str:
    lines = []
    total = 0
    for entry in reversed(history):           # most recent first
        line = f"{entry['role'].upper()}: {entry['content']}\n"
        if total + len(line) > max_chars:
            break
        lines.append(line)
        total += len(line)
    return "".join(reversed(lines))



def _build_prompt(doc_context: str, history_context: str, query: str, intent: str) -> str:

    """Build the full prompt sent to the LLaMA model."""
    doc_context     = doc_context[:DOC_CHAR_LIMIT]
    history_context = history_context[:HISTORY_CHAR_LIMIT]
    query           = query[:QUERY_CHAR_LIMIT]

    instruction = "Summarize using bullet points." if intent == "synthesis" else "Answer from context only. If not found, say so."

    return (
        f"{SYSTEM_ROLE}\n"           # role defined once at the top
        f"{instruction}\n\n"         # task-specific instruction
        f"### Context:\n{doc_context}\n\n"
        f"### History:\n{history_context}\n\n"
        f"### Question:\n{query}\n\n"
        "### Answer:"
    )