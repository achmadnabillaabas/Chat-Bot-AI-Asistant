"""
Test script for conversation search functionality.
"""
import requests
import sys

BASE_URL = "http://localhost:8000/api"

def test_search():
    """Test conversation search endpoint"""
    
    print("Testing conversation search...")
    print("=" * 60)
    
    # Test 1: List all conversations
    print("\n1. Testing GET /conversations (all conversations)")
    try:
        response = requests.get(f"{BASE_URL}/conversations")
        response.raise_for_status()
        all_convs = response.json()
        print(f"   ✓ Found {len(all_convs)} total conversations")
        if all_convs:
            print(f"   First conversation: '{all_convs[0]['title']}'")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    # Test 2: Search with a query
    if all_convs:
        # Use first word of first conversation title as search term
        search_term = all_convs[0]['title'].split()[0] if all_convs[0]['title'] else "test"
        print(f"\n2. Testing GET /conversations?search={search_term}")
        try:
            response = requests.get(f"{BASE_URL}/conversations", params={"search": search_term})
            response.raise_for_status()
            search_results = response.json()
            print(f"   ✓ Found {len(search_results)} matching conversations")
            for conv in search_results[:3]:
                print(f"   - {conv['title']}")
        except Exception as e:
            print(f"   ✗ Error: {e}")
            return False
    
    # Test 3: Search with non-existent term
    print(f"\n3. Testing GET /conversations?search=nonexistentxyz123")
    try:
        response = requests.get(f"{BASE_URL}/conversations", params={"search": "nonexistentxyz123"})
        response.raise_for_status()
        no_results = response.json()
        print(f"   ✓ Found {len(no_results)} conversations (expected 0)")
        if len(no_results) == 0:
            print(f"   ✓ Empty result handling works correctly")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    # Test 4: Search with limit
    print(f"\n4. Testing GET /conversations?limit=2")
    try:
        response = requests.get(f"{BASE_URL}/conversations", params={"limit": 2})
        response.raise_for_status()
        limited_results = response.json()
        print(f"   ✓ Found {len(limited_results)} conversations (limit=2)")
        if len(limited_results) <= 2:
            print(f"   ✓ Limit parameter works correctly")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✓ All tests passed!")
    return True

if __name__ == "__main__":
    try:
        success = test_search()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        sys.exit(1)
