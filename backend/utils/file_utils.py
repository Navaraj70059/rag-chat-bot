import hashlib
import uuid
import os

def generate_file_hash(file_content: bytes, length: int = 12) -> str:
    """
    Generate a short unique fingerprint for a file based on its content.
    Same file = same hash. Used to avoid duplicate uploads in ChromaDB.

    Args:
        file_content: Raw bytes of the file
        length: How many characters of the hash to use

    Returns:
        A short hex string (e.g. "a3f9c2b1e847")
    """
    return hashlib.sha256(file_content).hexdigest()[:length]


def save_temp_file(file_content: bytes) -> str:
    """
    Save file bytes to a temporary file on disk.
    Returns the temp filename so it can be processed and then deleted.

    Args:
        file_content: Raw bytes of the file

    Returns:
        Path to the temporary file
    """
    temp_filename = f"temp_{uuid.uuid4()}.pdf"
    with open(temp_filename, "wb") as f:
        f.write(file_content)
    return temp_filename


def delete_file_if_exists(filepath: str) -> None:
    """
    Safely delete a file if it exists. Used to clean up temp files.

    Args:
        filepath: Path to the file to delete
    """
    if os.path.exists(filepath):
        os.remove(filepath)


