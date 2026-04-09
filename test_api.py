import requests
import json

url = "http://localhost:8000/generate"
payload = {
    "task": "code",
    "user_input": "Write a python hello world",
    "user_id": 1001,
    "format_type": "structured"
}

print(f"Calling {url}...")
try:
    response = requests.post(url, json=payload, timeout=120)
    print(f"Status: {response.status_code}")
    print(f"Headers: {response.headers}")
    print(f"Content: {response.text[:500]}")
    try:
        print(f"JSON: {json.dumps(response.json(), indent=2)}")
    except:
        print("Response is not JSON")
except Exception as e:
    print(f"Request failed: {e}")
