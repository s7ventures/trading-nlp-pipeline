# cleaner.py
import re

def clean_text(text: str) -> str:
    """
    Cleans transcript text by removing timestamps, excessive spaces, etc.
    """
    # Remove lines like "12.34 - "
    text = re.sub(r"^\d+\.\d+\s*-\s*", "", text, flags=re.MULTILINE)

    # Remove bracketed timestamps if present [00:00:00]
    # text = re.sub(r"\[\d{2}:\d{2}:\d{2}\]", "", text)

    # Collapse multiple spaces
    text = re.sub(r"\s+", " ", text).strip()

    # Optional: convert to lowercase
    # text = text.lower()

    return text