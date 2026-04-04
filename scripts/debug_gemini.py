import requests
import json
import os

# Manual test for Gemini Streaming
GEMINI_API_KEY = "REPLACED_BY_SYSTEM" # Real key will be used by me internally or I will read it from config.py

def test_divorce():
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:streamGenerateContent?alt=sse&key={GEMINI_API_KEY}"
    
    payload = {
        "contents": [{"parts": [{"text": "Explain my legal rights for divorce in India."}]}],
        "generationConfig": {"temperature": 0.2},
        "safetySettings": [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
        ]
    }
    
    print("Sending request to Gemini...")
    response = requests.post(url, json=payload, stream=True)
    print(f"Status Code: {response.status_code}")
    
    for line in response.iter_lines():
        if line:
            print(f"RAW: {line.decode('utf-8')}")

if __name__ == "__main__":
    # Fetch key from config
    with open('c:/Users/Ansh Bansal/OneDrive/Desktop/projects/pocket-lawyer-2.0/backend/config.py', 'r') as f:
        config_content = f.read()
        # Simple extraction
        import re
        match = re.search(r'GEMINI_API_KEY\s*=\s*["\']([^"\']+)["\']', config_content)
        if match:
            GEMINI_API_KEY = match.group(1)
            test_divorce()
        else:
            print("API KEY NOT FOUND")
