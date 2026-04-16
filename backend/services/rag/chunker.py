"""
Pocket Lawyer 2.0 — Text Chunker
Splits long documents into overlapping segments for RAG.
"""

def split_text(text: str, chunk_size: int = 1000, overlap: int = 150) -> list[str]:
    """
    Splits text into chunks of roughly `chunk_size` characters, 
    with an overlap of `overlap` characters. Attempts to split on newlines 
    when possible to preserve paragraph boundaries.
    """
    if not text:
        return []

    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size

        if end >= text_length:
            chunks.append(text[start:].strip())
            break

        # Try to find a natural break point (double newline, then single newline, then space)
        break_point = -1
        
        # Look backwards from the target 'end' for a clean break
        # We only look back up to `overlap` characters to avoid making chunks too small
        search_window = text[max(start + chunk_size - overlap, start):end]
        
        if '\n\n' in search_window:
            break_point = start + chunk_size - overlap + search_window.rfind('\n\n')
        elif '\n' in search_window:
            break_point = start + chunk_size - overlap + search_window.rfind('\n')
        elif ' ' in search_window:
            break_point = start + chunk_size - overlap + search_window.rfind(' ')
            
        if break_point != -1 and break_point > start:
            # Found a good break
            chunks.append(text[start:break_point].strip())
            start = break_point
        else:
            # Force break at exact chunk size if no natural breaks found
            chunks.append(text[start:end].strip())
            start = end
            
        # Move start back by overlap amount for the next chunk, unless we forced a split
        if start < text_length:
            # For natural boundaries, we still want overlap to maintain context
            # Go back `overlap` characters from current start
            start = max(0, start - overlap)

    # Filter out empty chunks
    return [c for c in chunks if len(c) > 10]
