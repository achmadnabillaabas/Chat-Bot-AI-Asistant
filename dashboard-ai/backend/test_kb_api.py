"""
Test Knowledge Base API endpoints directly.
"""
import sys
import traceback
from app.core.database import SessionLocal
from app.api.knowledge_bases import list_knowledge_bases, get_default_user

def test_list_kb():
    """Test listing knowledge bases."""
    db = SessionLocal()
    try:
        print("Testing GET /api/knowledge-bases...")
        
        # Get user
        user = get_default_user(db)
        print(f"User: {user.id} - {user.email}")
        
        # Test the actual function
        import asyncio
        result = asyncio.run(list_knowledge_bases(db=db))
        
        print(f"Success! Total KBs: {result.total}")
        print(f"Items: {len(result.items)}")
        
        for item in result.items:
            print(f"  - {item.name} (id={item.id}, docs={item.document_count})")
        
    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}: {str(e)}")
        print("\nFull traceback:")
        traceback.print_exc()
        return False
    finally:
        db.close()
    
    return True

if __name__ == "__main__":
    success = test_list_kb()
    sys.exit(0 if success else 1)
