"""Test KB deletion to capture error."""
import requests

# Create KB
print("Creating KB...")
r = requests.post(
    "http://localhost:8000/api/knowledge-bases",
    json={"name": "Delete Test KB", "description": "Test"}
)
print(f"Create: {r.status_code}")
kb = r.json()
kb_id = kb["id"]
print(f"KB ID: {kb_id}")

# Try to delete
print(f"\nDeleting KB {kb_id}...")
r = requests.delete(f"http://localhost:8000/api/knowledge-bases/{kb_id}")
print(f"Delete status: {r.status_code}")

if r.status_code != 204:
    print(f"Error: {r.text}")
else:
    print("Success!")
