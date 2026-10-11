"""
Debug delete KB 500 error.
"""
import requests
import json
from pathlib import Path

BASE_URL = "http://localhost:8000/api"
HEADERS = {"Content-Type": "application/json"}

print("=" * 70)
print("DELETE KB DEBUG TEST")
print("=" * 70)

# Step 1: Create KB
print("\n[1] Creating KB...")
response = requests.post(
    f"{BASE_URL}/knowledge-bases",
    headers=HEADERS,
    json={"name": "Debug Delete Test", "description": "Test"}
)
if response.status_code in [200, 201]:
    kb = response.json()
    kb_id = kb["id"]
    collection_name = kb["collection_name"]
    print(f"OK KB created: id={kb_id}, collection={collection_name}")
else:
    print(f"FAILED: {response.text}")
    exit(1)

# Step 2: Upload document
print("\n[2] Uploading document...")
test_file = Path("test-delete.txt")
test_file.write_text("This is a test document for deletion.")

with open(test_file, "rb") as f:
    response = requests.post(
        f"{BASE_URL}/knowledge-bases/{kb_id}/documents",
        files={"file": ("test-delete.txt", f, "text/plain")}
    )

if response.status_code in [200, 201]:
    doc = response.json()
    doc_id = doc["id"]
    print(f"OK Document uploaded: id={doc_id}")
else:
    print(f"FAILED: {response.text}")
    exit(1)

import time
time.sleep(2)  # Wait for processing

# Step 3: Delete document first (like in main test)
print("\n[3] Deleting document...")
response = requests.delete(f"{BASE_URL}/knowledge-bases/{kb_id}/documents/{doc_id}")
print(f"Status: {response.status_code}")
if response.status_code == 204:
    print("OK Document deleted")
else:
    print(f"Response: {response.text}")

# Step 4: Try to delete KB
print("\n[4] Deleting KB (expecting 500 error)...")
response = requests.delete(f"{BASE_URL}/knowledge-bases/{kb_id}")
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
print(f"Headers: {dict(response.headers)}")

if response.status_code == 500:
    try:
        error_detail = response.json()
        print(f"\nError Detail (JSON):")
        print(json.dumps(error_detail, indent=2))
    except:
        print(f"\nError Detail (TEXT):")
        print(response.text)

# Cleanup
test_file.unlink(missing_ok=True)

print("\n" + "=" * 70)
print("TEST COMPLETE - Check backend logs for traceback")
print("=" * 70)
