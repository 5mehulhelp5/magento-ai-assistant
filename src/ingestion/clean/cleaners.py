import re
from html import unescape

def clean_text(text: str) -> str:
    """Clean HTML, extra spaces, and special entities from text."""
    if not text:
        return ""
    text = unescape(text)
    text = re.sub(r"<[^>]+>", " ", text)  # remove HTML tags
    text = re.sub(r"\s+", " ", text)      # normalize whitespace
    return text.strip()

def normalize_dimensions(text: str):
    match = re.search(r"(\d+)\s*[xX×]\s*(\d+)\s*(mm|cm|m)?", text)
    if match:
        return {
            "length": float(match.group(1)),
            "width": float(match.group(2)),
            "unit": match.group(3) or "mm",
        }
    return None

def normalize_capacity(text: str):
    match = re.search(r"(\d+\.?\d*)\s*(kg|lb|tons?)", text, re.IGNORECASE)
    if match:
        return {"value": float(match.group(1)), "unit": match.group(2).lower()}
    return None
