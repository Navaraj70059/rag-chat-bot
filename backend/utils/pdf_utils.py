"""
helpers.py
──────────
Reusable utility functions used across the project.
"""


from pypdf import PdfReader




def extract_text_from_pdf(filepath: str) -> list[str]:
    """
    Extract text from each page of a PDF file.

    Args:
        filepath: Path to the PDF file

    Returns:
        List of strings, one per page (empty pages are skipped)
    """
    reader = PdfReader(filepath)
    chunks = []
    for page in reader.pages:
        content = page.extract_text()
        if content:
            chunks.append(content)
    return chunks

