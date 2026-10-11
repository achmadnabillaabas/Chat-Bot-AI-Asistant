import requests

# Create test file
with open("test-policy.txt", "w") as f:
    f.write("Employees receive 12 days of annual leave per year. All vacation requests must be submitted at least 2 weeks in advance.")

# Upload
with open("test-policy.txt", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/knowledge-bases/4/documents",
        files={"file": ("test-policy.txt", f, "text/plain")}
    )

print(f"Status: {response.status_code}")
result = response.json()
print(f"ID: {result['id']}")
print(f"Filename: {result['filename']}")
print(f"Status: {result['status']}")
