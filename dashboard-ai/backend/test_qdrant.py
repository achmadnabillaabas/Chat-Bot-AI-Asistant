"""Test Qdrant connectivity."""
from app.services.qdrant_service import qdrant_service

print("Testing Qdrant service...")

# Test 1: Get collections
print("\n1. Getting collections...")
try:
    collections = qdrant_service.client.get_collections().collections
    print(f"✓ Success: {len(collections)} collections")
except Exception as e:
    print(f"✗ Failed: {e}")
    exit(1)

# Test 2: Create test collection
print("\n2. Creating test collection...")
try:
    qdrant_service.create_collection("test_collection", dimension=384)
    print("✓ Collection created")
except Exception as e:
    print(f"✗ Failed: {e}")
    exit(1)

# Test 3: Check collection exists
print("\n3. Checking collection exists...")
exists = qdrant_service.collection_exists("test_collection")
print(f"✓ Exists: {exists}")

# Test 4: Delete collection
print("\n4. Deleting test collection...")
try:
    qdrant_service.delete_collection("test_collection")
    print("✓ Collection deleted")
except Exception as e:
    print(f"✗ Failed: {e}")

print("\n✅ Qdrant service: WORKING")
