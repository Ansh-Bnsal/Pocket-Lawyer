import os
import json
import numpy as np
import faiss

# Each case gets its own FAISS index to ensure airtight data isolation.
BASE_INDEX_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'rag_indices')
os.makedirs(BASE_INDEX_DIR, exist_ok=True)

class VectorStore:
    def __init__(self, dimension: int = 768):
        self.dimension = dimension # Gemini text-embedding-004 is 768d

    def _get_paths(self, case_id: int):
        idx_path = os.path.join(BASE_INDEX_DIR, f"case_{case_id}.faiss")
        meta_path = os.path.join(BASE_INDEX_DIR, f"case_{case_id}_meta.json")
        return idx_path, meta_path

    def _load_index(self, case_id: int):
        idx_path, meta_path = self._get_paths(case_id)
        if os.path.exists(idx_path) and os.path.exists(meta_path):
            index = faiss.read_index(idx_path)
            with open(meta_path, 'r', encoding='utf-8') as f:
                return index, json.load(f)
        else:
            # L2 distance index for FAISS
            return faiss.IndexFlatL2(self.dimension), []

    def _save_index(self, case_id: int, index, metadata: list):
        idx_path, meta_path = self._get_paths(case_id)
        faiss.write_index(index, idx_path)
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f)

    def add_documents(self, case_id: int, doc_id: int, filename: str, chunks: list[str], embeddings: list[list[float]]):
        """
        Adds new document chunks to the case's vector index.
        """
        if not chunks or not embeddings:
            return
            
        index, meta_list = self._load_index(case_id)
        
        # Convert embeddings to float32 numpy array as required by FAISS
        embeddings_np = np.array(embeddings).astype('float32')
        
        # Add to FAISS index
        index.add(embeddings_np)
        
        # Add to metadata
        for i, chunk in enumerate(chunks):
            meta_list.append({
                "doc_id": doc_id,
                "filename": filename,
                "chunk_index": i,
                "text": chunk
            })
            
        self._save_index(case_id, index, meta_list)
        print(f"[VectorStore] Added {len(chunks)} chunks to Case #{case_id} FAISS index.")

    def search(self, case_id: int, query_embedding: list[float], top_k: int = 4) -> list[dict]:
        """
        Retrieves the top_k most similar chunks for a given case.
        """
        index, meta_list = self._load_index(case_id)
        
        if index.ntotal == 0:
            return []
            
        # Format query for FAISS (needs to be 2D array)
        q_np = np.array([query_embedding]).astype('float32')
        
        # Ensure k is not larger than total vectors
        k = min(top_k, index.ntotal)
        
        # Search
        distances, indices = index.search(q_np, k)
        
        results = []
        for j in range(k):
            idx = indices[0][j]
            if idx != -1 and idx < len(meta_list): # Check bounds and valid idx
                meta = dict(meta_list[idx])
                meta["distance"] = float(distances[0][j])
                results.append(meta)
                
        return results

store = VectorStore()
