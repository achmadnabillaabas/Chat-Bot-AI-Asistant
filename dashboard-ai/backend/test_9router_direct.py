"""
Direct 9Router API test script.
Tests the exact same request that the application makes.
"""
import asyncio
import httpx
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

NINEROUTER_BASE_URL = os.getenv("NINEROUTER_BASE_URL", "http://localhost:20128")
NINEROUTER_API_KEY = os.getenv("NINEROUTER_API_KEY", "")


async def test_9router_direct():
    """Test direct connection to 9Router with ai-general combo."""
    
    print("=" * 60)
    print("9Router Direct Test")
    print("=" * 60)
    print(f"Base URL: {NINEROUTER_BASE_URL}")
    print(f"API Key: {'[SET]' if NINEROUTER_API_KEY else '[NOT SET]'}")
    print(f"API Key Length: {len(NINEROUTER_API_KEY)}")
    print()
    
    if not NINEROUTER_API_KEY:
        print("❌ ERROR: NINEROUTER_API_KEY not set in environment")
        return False
    
    # Test 1: List models
    print("Test 1: List Models")
    print("-" * 60)
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{NINEROUTER_BASE_URL}/v1/models",
                headers={
                    "Authorization": f"Bearer {NINEROUTER_API_KEY}",
                    "Content-Type": "application/json"
                }
            )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                models = data.get("data", [])
                print(f"✅ Models endpoint accessible")
                print(f"Total models: {len(models)}")
                
                # List combos
                combos = [m for m in models if m.get("id", "").startswith("ai-")]
                print(f"Combo models: {len(combos)}")
                
                for combo in combos[:5]:  # Show first 5
                    print(f"  - {combo.get('id')}")
                
                # Check if ai-general exists
                ai_general = any(m.get("id") == "ai-general" for m in models)
                print(f"'ai-general' available: {ai_general}")
                
                # Check if combowombojumbo exists
                combowombojumbo = any(m.get("id") == "combowombojumbo" for m in models)
                print(f"'combowombojumbo' available: {combowombojumbo}")
                print()
            else:
                print(f"❌ Models endpoint failed: {response.status_code}")
                print(f"Response: {response.text[:500]}")
                return False
                
    except Exception as e:
        print(f"❌ Error connecting to models endpoint: {e}")
        return False
    
    # Test 2: Chat completion with ai-general
    print("Test 2: Chat Completion (ai-general)")
    print("-" * 60)
    
    # Use combowombojumbo if available, otherwise ai-general
    test_model = "combowombojumbo"  # Try this first
    
    # Check if combowombojumbo is available from Test 1
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{NINEROUTER_BASE_URL}/v1/models",
                headers={
                    "Authorization": f"Bearer {NINEROUTER_API_KEY}",
                    "Content-Type": "application/json"
                }
            )
            if response.status_code == 200:
                data = response.json()
                models = data.get("data", [])
                model_ids = [m.get("id") for m in models]
                
                if "combowombojumbo" in model_ids:
                    test_model = "combowombojumbo"
                    print(f"Using model: combowombojumbo (available)")
                elif "ai-general" in model_ids:
                    test_model = "ai-general"
                    print(f"Using model: ai-general (fallback)")
                else:
                    test_model = model_ids[0] if model_ids else "ai-general"
                    print(f"Using model: {test_model} (first available)")
    except:
        test_model = "ai-general"
        print(f"Using model: ai-general (default)")
    
    print()
    
    payload = {
        "model": test_model,
        "messages": [
            {"role": "user", "content": "Hello, say 'test successful' if you can read this."}
        ],
        "temperature": 0.7
    }
    
    print(f"Payload: {payload}")
    print()
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{NINEROUTER_BASE_URL}/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {NINEROUTER_API_KEY}",
                    "Content-Type": "application/json"
                },
                json=payload
            )
            
            print(f"Status: {response.status_code}")
            print(f"Headers: {dict(response.headers)}")
            print()
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Chat completion successful!")
                print()
                print("Response structure:")
                print(f"  - id: {data.get('id')}")
                print(f"  - object: {data.get('object')}")
                print(f"  - model: {data.get('model')}")
                print(f"  - choices: {len(data.get('choices', []))}")
                
                if data.get("choices"):
                    choice = data["choices"][0]
                    message = choice.get("message", {})
                    content = message.get("content", "")
                    print()
                    print("AI Response:")
                    print(f"  {content}")
                
                usage = data.get("usage", {})
                if usage:
                    print()
                    print("Token Usage:")
                    print(f"  - prompt_tokens: {usage.get('prompt_tokens')}")
                    print(f"  - completion_tokens: {usage.get('completion_tokens')}")
                    print(f"  - total_tokens: {usage.get('total_tokens')}")
                
                print()
                print("=" * 60)
                print("✅ ALL TESTS PASSED")
                print("=" * 60)
                return True
                
            else:
                print(f"❌ Chat completion failed: {response.status_code}")
                print()
                print("Response body:")
                try:
                    error_data = response.json()
                    print(f"{error_data}")
                except:
                    print(f"{response.text}")
                
                print()
                print("=" * 60)
                print("❌ TEST FAILED")
                print("=" * 60)
                return False
                
    except httpx.TimeoutException:
        print("❌ Request timeout (120s)")
        return False
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_9router_direct())
    sys.exit(0 if success else 1)
