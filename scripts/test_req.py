import requests

data = {
    "message": "Hi",
    "is_transient": "true"
}

resp = requests.post("http://127.0.0.1:5000/api/chat", json=data)
print(resp.text)
