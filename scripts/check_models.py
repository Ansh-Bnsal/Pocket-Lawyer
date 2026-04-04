import requests
import json
from config import GEMINI_API_KEY
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={GEMINI_API_KEY}"
response = requests.get(url)
print(response.status_code)
for model in response.json().get('models', []):
    print(model['name'])
