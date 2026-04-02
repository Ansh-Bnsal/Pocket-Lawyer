"""
Pocket Lawyer 2.0 — Google Gemini Provider
Handles direct multimodal (text + image/PDF) requests.
"""
import requests
import json
from .base import BaseProvider
from config import GEMINI_API_KEY

class GeminiProvider(BaseProvider):
    def generate(self, prompt: str, file_data: dict = None, model: str = None) -> str:
        """
        Send a multimodal prompt to Gemini 2.0 Flash.
        """
        api_key = GEMINI_API_KEY
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not configured.")

        # Default to Gemini 2.5 Flash (Bypasses 2.0-flash quota exhaustion)
        model_name = model if model else "gemini-2.5-flash"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"

        # 🧩 BUILD MULTIMODAL PAYLOAD
        # Gemini expects a list of parts: text, inline_data, etc.
        parts = [{"text": prompt}]
        
        if file_data and file_data.get('base64'):
            parts.append({
                "inline_data": {
                    "mime_type": file_data.get('mime_type', 'application/pdf'),
                    "data": file_data.get('base64')
                }
            })

        payload = {
            "contents": [{"parts": parts}],
            "generationConfig": {
                "temperature": 0.2,
                "responseMimeType": "application/json" # Always JSON for our Normalizer to handle
            }
        }

        try:
            response = requests.post(url, json=payload, timeout=45)
            response.raise_for_status()
            data = response.json()
            
            # Extract raw block from candidate (assuming single candidate)
            raw_text = data['candidates'][0]['content']['parts'][0]['text']
            return raw_text
        except Exception as e:
            raise RuntimeError(f"Gemini API Error: {str(e)}")
    def stream_generate(self, prompt: str, file_data: dict = None, model: str = None):
        """
        Stream text chunks from Gemini using Server-Sent Events (SSE).
        """
        api_key = GEMINI_API_KEY
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not configured.")

        model_name = model if model else "gemini-2.5-flash"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:streamGenerateContent?alt=sse&key={api_key}"

        parts = [{"text": prompt}]
        if file_data and file_data.get('base64'):
            parts.append({
                "inline_data": {
                    "mime_type": file_data.get('mime_type', 'application/pdf'),
                    "data": file_data.get('base64')
                }
            })

        payload = {
            "contents": [{"parts": parts}],
            "generationConfig": {
                "temperature": 0.2
                # We don't specify JSON mime type for streaming text
            }
        }

        try:
            response = requests.post(url, json=payload, stream=True, timeout=60)
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    if decoded_line.startswith('data:'):
                        json_str = decoded_line[5:].strip()
                        if not json_str:
                            continue
                        try:
                            data = json.loads(json_str)
                            if 'candidates' in data and len(data['candidates']) > 0:
                                parts = data['candidates'][0].get('content', {}).get('parts', [])
                                if parts and 'text' in parts[0]:
                                    yield parts[0]['text']
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            yield f"\n[System Error: Stream failed: {str(e)}]"
