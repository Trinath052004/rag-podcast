import re
from typing import List

def clean_text(text: str) -> str:
    """Clean and normalize text for processing"""
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    # Remove special characters except basic punctuation
    text = re.sub(r'[^\w\s.,;:!?-]', '', text)
    return text

def split_into_sentences(text: str) -> List[str]:
    """Split text into sentences using basic heuristics"""
    # Split on common sentence terminators followed by whitespace or capital letter
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
    return [s.strip() for s in sentences if s.strip()]

def normalize_text(text: str) -> str:
    """Normalize text for embedding generation"""
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
    return text

def truncate_text(text: str, max_length: int = 500) -> str:
    """Truncate text to maximum length while preserving complete sentences"""
    if len(text) <= max_length:
        return text

    sentences = split_into_sentences(text)
    truncated = ""
    char_count = 0

    for sentence in sentences:
        if char_count + len(sentence) <= max_length:
            truncated += sentence + " "
            char_count += len(sentence) + 1
        else:
            break

    return truncated.strip()
