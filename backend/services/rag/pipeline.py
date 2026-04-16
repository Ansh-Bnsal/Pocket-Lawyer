"""
Pocket Lawyer 2.0 — Native Document RAG Pipeline
Orchestrates document chunking, embedding, indexing, and retrieval.
"""
from .chunker import split_text
from .embeddings import embedder
from .vector_store import store

def index_case_document(case_id: int, doc_id: int, filename: str, extracted_text: str):
    """
    Called after a document is uploaded. 
    1. Chunks text
    2. Embeds chunks
    3. Saves to FAISS
    """
    if not extracted_text or len(extracted_text.strip()) == 0:
        return
        
    try:
        # 1. Chunk
        chunks = split_text(extracted_text)
        if not chunks:
            return
            
        print(f"[RAG Pipeline] Chunks created: {len(chunks)} for doc '{filename}'")
        
        # 2. Embed
        embeddings = embedder.embed_batch(chunks)
        print(f"[RAG Pipeline] Created {len(embeddings)} embeddings.")
        
        # 3. Index
        store.add_documents(case_id, doc_id, filename, chunks, embeddings)
        
    except Exception as e:
        print(f"[RAG Pipeline Error - Indexing] {e}")


def retrieve_context(case_id: int, query: str, top_k: int = 4) -> str:
    """
    Searches the per-case vector index for the top-k paragraphs matching the query.
    Returns a unified string of context.
    """
    if not query or not case_id:
        return ""
        
    try:
        # 1. Embed query (use RETRIEVAL_QUERY task type)
        query_vector = embedder.embed_text(query, task_type="RETRIEVAL_QUERY")
        
        # 2. Search FAISS
        results = store.search(case_id, query_vector, top_k)
        
        if not results:
            return ""
            
        # 3. Format context string
        context_parts = []
        context_parts.append(f"\n--- RAG RETRIEVED DOCUMENT CONTEXT FOR CASE #{case_id} ---")
        
        for r in results:
            # You can check r['distance'] here if you want to apply a strict semantic similarity cutoff.
            # Using L2 distance, closer to 0 is more similar.
            context_parts.append(f"[From: {r['filename']}]\n{r['text']}")
            
        context_parts.append("--- END RETRIEVED CONTEXT ---")
        return "\n\n".join(context_parts)
        
    except Exception as e:
        print(f"[RAG Pipeline Error - Retrieval] {e}")
        return ""
