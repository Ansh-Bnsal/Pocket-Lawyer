import json
import requests
from .base import AIProvider
from config import GEMINI_API_KEY

class GeminiProvider(AIProvider):
    """
    Google Gemini Provider (Flash 1.5).
    Optimized for JSON extraction and streaming.
    """
    def __init__(self, model_name="gemini-1.5-flash"):
        self.model_name = model_name
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}"

    def generate(self, prompt: str, file_data: dict = None) -> str:
        url = f"{self.base_url}:generateContent?key={GEMINI_API_KEY}"
        
        # [Multimodal] BUILD MULTIMODAL PAYLOAD
        parts = [{"text": prompt}]
        if file_data:
            parts.append({
                "inline_data": {
                    "mime_type": file_data["mime_type"],
                    "data": file_data["base64"]
                }
            })

        payload = {
            "contents": [{"parts": parts}],
            "generationConfig": {
                "temperature": 0.2,
                "responseMimeType": "application/json"
            }
        }

        try:
            resp = requests.post(url, json=payload, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            print(f"[Gemini Error] {str(e)}")
            raise e

    def stream_generate(self, prompt: str, file_data: dict = None):
        url = f"{self.base_url}:streamGenerateContent?key={GEMINI_API_KEY}&alt=sse"
        
        parts = [{"text": prompt}]
        if file_data:
            parts.append({
                "inline_data": {
                    "mime_type": file_data["mime_type"],
                    "data": file_data["base64"]
                }
            })

        payload = {
            "contents": [{"parts": parts}],
            "generationConfig": {
                "temperature": 0.2
            }
        }

        try:
            # Note: We use stream=True for the request
            with requests.post(url, json=payload, timeout=60, stream=True) as resp:
                resp.raise_for_status()
                for line in resp.iter_lines():
                    if not line: continue
                    
                    line_str = line.decode('utf-8').strip()
                    if line_str.startswith("data:"): line_str = line_str[5:].strip()
                    
                    # Gemini SSE is a JSON array of objects
                    try:
                        # Raw stream contains [{},{},...] - very messy to parse line by line
                        # Actually, Gemini 1.5 stream usually returns JSON objects directly per chunk
                        # Let's handle the direct JSON approach
                        chunk = json.loads(line_str)
                        text_chunk = chunk["candidates"][0]["content"]["parts"][0]["text"]
                        if text_chunk:
                            yield text_chunk
                    except:
                        # Some lines might be control characters like '[' or ','
                        continue
        except Exception as e:
            print(f"[Gemini Stream Error] {str(e)}")
            yield f"[Connection Lost: {str(e)}]"
