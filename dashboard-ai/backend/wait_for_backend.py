"""
Wait for backend to be ready.
"""
import requests
import time
import sys

url = "http://localhost:8000/api/models"
max_wait = 30

print("Waiting for backend to be ready...")
for i in range(max_wait):
    try:
        response = requests.get(url, timeout=2)
        if response.status_code == 200:
            print(f"✅ Backend ready!")
            sys.exit(0)
    except:
        pass
    
    if i % 5 == 0 and i > 0:
        print(f"   Still waiting... ({i}s)")
    time.sleep(1)

print("❌ Backend not ready after 30s")
print("Please start backend manually:")
print("  cd backend")
print("  .\\venv\\Scripts\\python.exe -m uvicorn app.main:app --reload")
sys.exit(1)
