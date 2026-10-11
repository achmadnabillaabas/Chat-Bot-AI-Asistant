"""
Single test to debug knowledge_base_id in token usage.
"""
import requests
import json
from pathlib import Path
import time

BASE_URL = "http://localhost:8000/api"
HEADERS = {"Content-Type": "application/json"}

print("=" * 70)
print("SINGLE TEST: KB_ID IN TOKEN USAGE")
print("=" * 70)

# Create KB
print("\n[1] Creating KB...")
response = requests.post(
    f"{BASE_URL}/knowledge-bases",
    headers=HEADERS,
    json={"name": "Debug KB ID", "description": "Test"}
)
kb = response.json()
kb_id = kb["id"]
print(f"OK KB created: id={kb_id}")

# Upload doc
print("\n[2] Uploading document...")
test_file = Path("test-kb-id.txt")
test_file.write_text("The company provides health insurance.")

with open(test_file, "rb") as f:
    response = requests.post(
        f"{BASE_URL}/knowledge-bases/{kb_id}/documents",
        files={"file": ("test-kb-id.txt", f, "text/plain")}
    )

doc = response.json()
print(f"OK Document uploaded: id={doc['id']}")

# Wait for processing
print("\n[3] Waiting for processing...")
time.sleep(2)

# Chat with RAG ON and this specific KB
print(f"\n[4] Chat with RAG ON, KB_ID={kb_id}...")
chat_request = {
    "message": "What does the company provide?",
    "knowledge_base_id": kb_id,
    "rag_enabled": True,
    "model": "combowombojumbo"
}

print(f"Request payload:")
print(json.dumps(chat_request, indent=2))

response = requests.post(
    f"{BASE_URL}/chat",
    headers=HEADERS,
    json=chat_request
)

if response.status_code == 200:
    result = response.json()
    print(f"OK Chat response received")
    print(f"   Answer: {result['message']['content'][:100]}...")
    print(f"   Sources: {len(result.get('sources', []))}")
else:
    print(f"FAILED: {response.text}")

# Check token usage
print("\n[5] Checking token_usage...")
response = requests.get(f"{BASE_URL}/analytics/usage/requests?page_size=1")
if response.status_code == 200:
    usage = response.json()
    if usage['items']:
        latest = usage['items'][0]
        print(f"Latest token_usage record:")
        print(f"   ID: {latest['id']}")
        print(f"   rag_enabled: {latest['rag_enabled']}")
        print(f"   knowledge_base_id: {latest.get('knowledge_base_id')}")
        print(f"   model: {latest['model']}")
        print(f"   request_type: {latest['request_type']}")
        
        # Verify
        if latest['rag_enabled'] and latest.get('knowledge_base_id') == kb_id:
            print(f"\n✅ CORRECT: KB ID is stored!")
        elif latest['rag_enabled'] and not latest.get('knowledge_base_id'):
            print(f"\n❌ BUG: RAG enabled but KB ID is NULL!")
            print(f"   Expected: kb_id={kb_id}")
            print(f"   Got: kb_id=None")
        else:
            print(f"\n⚠️  Different record retrieved")

# Cleanup
print("\n[6] Cleanup...")
response = requests.delete(f"{BASE_URL}/knowledge-bases/{kb_id}")
print(f"KB deleted: {response.status_code}")

test_file.unlink(missing_ok=True)

print("\n" + "=" * 70)
print("CHECK BACKEND LOGS FOR:")
print("  'Creating token usage record'")
print("  'Saved token usage'")
print("=" * 70)
