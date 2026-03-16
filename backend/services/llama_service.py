"""
llama_service.py
────────────────
Handles loading and running the local LLaMA model.
Model settings come from config.py (which reads from .env).
"""

from llama_cpp import Llama
from backend.config import  MAX_TOKENS_SPECIFIC, MODEL_PATH, N_CTX, N_THREADS, N_BATCH, N_GPU_LAYERS

# Load model once when the app starts (not on every request)
llm = Llama(
    model_path=MODEL_PATH,
    n_ctx=N_CTX,
    n_threads=N_THREADS,
    n_batch=N_BATCH,
    n_gpu_layers=N_GPU_LAYERS
)


def generate_answer(prompt: str, max_tokens: int = MAX_TOKENS_SPECIFIC) -> str:
    """
    Send a prompt to LLaMA and return the generated answer.

    Args:
        prompt: The full prompt string including context and question
        max_tokens: Maximum number of tokens to generate

    Returns:
        The model's response as a string
    """
    output = llm(
        prompt,
        max_tokens=max_tokens,
        stop=["User:", "Assistant:", "Human:"],
        temperature=0.1
    )
    return output["choices"][0]["text"].strip() # type: ignore
