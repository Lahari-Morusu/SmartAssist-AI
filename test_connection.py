import requests

print("Testing connection...")

response = requests.get("http://127.0.0.1:11434/api/tags", timeout=10)

print(response.status_code)
print(response.text[:500])
