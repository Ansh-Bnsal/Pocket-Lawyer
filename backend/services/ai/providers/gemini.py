import json
import time
import requests
from .base import AIProvider
from config import GEMINI_API_KEY
from ..exceptions import RateLimitException, ServiceUnavailableException, AIException

class GeminiProvider(AIProvider):
    """
    Google Gemini Provider (Flash 1.5).
    Optimized for JSON extraction and resilience against 429 Rate-Limits.
    """
    def __init__(self, model_name="gemini-2.5-flash"):
        self.model_name = "gemini-2.5-flash" # Use stable version explicitly
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}"

    def _call(self, method, url, payload, stream=False):
        """
        [Resilience Layer] Performs exponential backoff on 429 and 503 errors.
        """
        retries = 3
        backoff = 1.5
        for i in range(retries + 1):
            try:
                resp = requests.post(url, json=payload, timeout=60, stream=stream)
                
                if resp.status_code == 429:
                    print(f"DEBUG: 429 Detailed Response -> {resp.text}")
                    if i < retries:
                        print(f"[Gemini 429] Rate limited. Retrying in {backoff}s... ({retries - i} left)")
                        time.sleep(backoff)
                        backoff *= 2
                        continue
                    raise RateLimitException("api_limit_exhausted")
                
                if resp.status_code == 503:
                    print(f"DEBUG: 503 Detailed Response -> {resp.text}")
                    if i < retries:
                        print(f"[Gemini 503] Server busy. Retrying in {backoff}s... ({retries - i} left)")
                        time.sleep(backoff)
                        backoff *= 2
                        continue
                    raise ServiceUnavailableException("Gemini API is currently overloaded.")
                
                resp.raise_for_status()
                return resp
            except requests.exceptions.RequestException as e:
                print(f"[Network/Request Error Triggered] Resulted in: {str(e)}")
                if hasattr(e, 'response') and e.response is not None and e.response.status_code == 429:
                    if i < retries:
                        time.sleep(backoff)
                        backoff *= 2
                        continue
                if i < retries:
                    time.sleep(backoff)
                    backoff *= 2
                    continue
                raise AIException(f"Network error in AI Provider: {str(e)}")

    def generate(self, prompt: str, file_data: dict = None, history: list = None, api_key: str = None) -> str:
        k = (api_key or GEMINI_API_KEY).strip()
        url = f"{self.base_url}:generateContent?key={k}"
        
        # [System] System Instruction (The Instructions/Template)
        payload = {
            "system_instruction": {"parts": [{"text": prompt}]},
            "generationConfig": {"temperature": 0.2, "responseMimeType": "application/json"},
            "contents": []
        }

        # [History] Add conversation history
        if history:
            for item in history:
                role = "user" if item["role"] == "user" else "model"
                content = item.get("content", "")
                if content:
                    payload["contents"].append({"role": role, "parts": [{"text": content}]})

        # [Input] Final message (if file_data is present, it's usually on the last message)
        # Assuming the Orchestrator sends the current message as a single string
        # If history is empty, we still need at least one user message in contents
        payload["contents"].append({"role": "user", "parts": [{"text": "Please process the request above based on our conversation."}]}) if history else payload["contents"].append({"role": "user", "parts": [{"text": "Please process."}]})

        if file_data:
            payload["contents"][-1]["parts"].append({"inline_data": {"mime_type": file_data["mime_type"], "data": file_data["base64"]}})

        payload["safetySettings"] = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
        ]
        
        resp = self._call("POST", url, payload)
        data = resp.json()
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError):
            print(f"[Gemini Error Response] {json.dumps(data)}")
            return "I apologize, but I encountered an error in the AI response."

    def stream_generate(self, prompt: str, file_data: dict = None, history: list = None, api_key: str = None):
        k = api_key or GEMINI_API_KEY
        url = f"{self.base_url}:streamGenerateContent?key={k}&alt=sse"
        
        payload = {
            "system_instruction": {"parts": [{"text": prompt}]},
            "generationConfig": {"temperature": 0.1},
            "contents": []
        }

        if history:
            for item in history:
                role = "user" if item["role"] == "user" else "model"
                content = item.get("content", "")
                if content:
                    payload["contents"].append({"role": role, "parts": [{"text": content}]})
        
        # Final trigger
        payload["contents"].append({"role": "user", "parts": [{"text": "Continue the conversation."}]})

        if file_data:
            payload["contents"][-1]["parts"].append({"inline_data": {"mime_type": file_data["mime_type"], "data": file_data["base64"]}})

        payload["safetySettings"] = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
        ]

        resp = self._call("POST", url, payload, stream=True)
        try:
            for line in resp.iter_lines():
                if not line: continue
                line_str = line.decode('utf-8').strip()
                if line_str.startswith("data:"): 
                    data_str = line_str[5:].strip()
                    if not data_str or data_str in ["[", "]", ","]: continue
                    try:
                        chunk = json.loads(data_str)
                        if "candidates" in chunk:
                            text_chunk = chunk["candidates"][0]["content"]["parts"][0].get("text", "")
                            if text_chunk:
                                yield text_chunk
                    except: continue
        except Exception as e:
            if "api_limit_exhausted" in str(e):
                raise RateLimitException("api_limit_exhausted")
            raise AIException(f"Stream interrupted: {str(e)}")
