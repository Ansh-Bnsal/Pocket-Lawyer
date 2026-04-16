import requests
from config import GEMINI_API_KEY
import time

class Embeddings:
    """
    Interfaces with Google Gemini's text-embedding-004 model.
    """
    def __init__(self):
        self.model_name = "text-embedding-004"
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:embedContent"

    def embed_text(self, text: str, task_type: str = "RETRIEVAL_DOCUMENT") -> list[float]:
        """
        Embeds a single string into a vector.
        task_type: 'RETRIEVAL_DOCUMENT' for indexing, 'RETRIEVAL_QUERY' for searching.
        """
        url = f"{self.base_url}?key={GEMINI_API_KEY}"
        payload = {
            "model": f"models/{self.model_name}",
            "content": {
                "parts": [{"text": text}]
            },
            "taskType": task_type
        }
        
        # Simple backoff
        for i in range(3):
            resp = requests.post(url, json=payload, timeout=30)
            if resp.status_code in [429, 503]:
                time.sleep(1.5 * (i + 1))
                continue
            resp.raise_for_status()
            data = resp.json()
            return data.get("embedding", {}).get("values", [])
            
        raise Exception("Failed to embed text: Rate Limit Exceeded")

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """
        Batch call for Gemini Embeddings.
        Note: The batch API URL is slightly different.
        """
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:batchEmbedContents?key={GEMINI_API_KEY}"
        
        requests_payload = []
        for t in texts:
            requests_payload.append({
                "model": f"models/{self.model_name}",
                "content": {"parts": [{"text": t}]},
                "taskType": "RETRIEVAL_DOCUMENT"
            })
            
        payload = {"requests": requests_payload}
        
        for i in range(3):
            resp = requests.post(url, json=payload, timeout=60)
            if resp.status_code in [429, 503]:
                time.sleep(2 * (i + 1))
                continue
            resp.raise_for_status()
            data = resp.json()
            
            embeddings = []
            for e in data.get("embeddings", []):
                embeddings.append(e.get("values", []))
            return embeddings
            
        raise Exception("Failed to batch embed texts: Rate Limit Exceeded")

# Global instance
embedder = Embeddings()
