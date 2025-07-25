import pdfplumber
from typing import List

def load_pdf_text(filepath: str) -> str:
    """Load text content from PDF"""
    text = ""
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

def chunk_text(text: str, chunk_size: int = 500) -> List[str]:
    """Split text into chunks of approximately chunk_size characters"""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        if end >= len(text):
            chunks.append(text[start:])
            break
        
        # Try to find a sentence boundary
        boundary = max(
            text.rfind('.', start, end),
            text.rfind('\n', start, end),
            text.rfind(' ', start, end)
        )
        
        if boundary > start:
            chunks.append(text[start:boundary + 1])
            start = boundary + 1
        else:
            chunks.append(text[start:end])
            start = end
    
    return chunks