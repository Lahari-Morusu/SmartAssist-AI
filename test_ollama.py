import requests
import json

print("Starting test...")

response = requests.post(
    "http://127.0.0.1:11434/api/generate",
    json={
        "model": "llama3:latest",
        "prompt": "What is Python?",
        "stream": False
    },
    timeout=300
)

print("Status:", response.status_code)

data = response.json()

print(json.dumps(data, indent=2))