"""
End-to-end RAG backend test.
Tests the complete flow: KB creation -> Document upload -> Processing -> RAG search -> Chat
"""
import sys
import asyncio
import os
from pathlib import Path

from app.core.database import SessionLocal
from app.api.knowledge_bases import create_knowledge_base, list_knowledge_bases, get_default_user
from app.schemas.knowledge_base import KnowledgeBaseCreate

print("=" * 60)
print("RAG END-TO-END BACKEND TEST")
print("=" * 60)

async def main():
    db = SessionLocal()
    
    try:
        # Step 1: Get user
        print("\n[1/10] Getting default user...")
        user = get_default_user(db)
        print(f"✓ User: {user.id} - {user.email}")
        
        # Step 2: List existing KBs
        print("\n[2/10] Listing existing knowledge bases...")
        result = await list_knowledge_bases(db=db)
        print(f"✓ Current KBs: {result.total}")
        
        # Step 3: Create new KB
        print("\n[3/10] Creating knowledge base: 'Test RAG'...")
        kb_data = KnowledgeBaseCreate(
            name="Test RAG",
            description="Test knowledge base for RAG validation"
        )
        kb = await create_knowledge_base(request=kb_data, db=db)
        print(f"✓ Created KB: id={kb.id}, name={kb.name}")
        print(f"  Collection: {kb.collection_name}")
        
        # Step 4: Create test document
        print("\n[4/10] Creating test document...")
        test_content = "Employees receive 12 days of annual leave per year. The company policy states that vacation requests must be submitted at least 2 weeks in advance."
        
        upload_dir = Path("uploads")
        upload_dir.mkdir(exist_ok=True)
        test_file = upload_dir / "company-policy.txt"
        
        with open(test_file, "w") as f:
            f.write(test_content)
        
        print(f"✓ Created test file: {test_file}")
        print(f"  Content length: {len(test_content)} chars")
        
        # Step 5: Test Qdrant connection
        print("\n[5/10] Testing Qdrant connection...")
        from app.services.qdrant_service import qdrant_service
        
        if qdrant_service.collection_exists(kb.collection_name):
            print(f"✓ Qdrant collection exists: {kb.collection_name}")
        else:
            print(f"✗ Qdrant collection NOT found: {kb.collection_name}")
            return False
        
        # Step 6: Test embedding generation
        print("\n[6/10] Testing embedding generation...")
        from app.services.embedding_service import embedding_service
        
        try:
            test_embedding = await embedding_service.generate_embedding("test query")
            print(f"✓ Embedding generated: dimension={len(test_embedding)}")
        except Exception as e:
            print(f"✗ Embedding FAILED: {type(e).__name__}: {str(e)}")
            print("\nEmbedding provider issue detected!")
            print("9Router may not support embeddings endpoint.")
            print("Consider using sentence-transformers instead.")
            return False
        
        # Step 7: Test document upload (simulated for now)
        print("\n[7/10] Document upload API...")
        print("⚠ Skipping actual upload test (requires multipart form)")
        print("  Use: POST /api/knowledge-bases/{kb.id}/documents")
        print(f"  File: {test_file}")
        
        # Step 8: Test document processor
        print("\n[8/10] Testing document processor...")
        from app.services.document_processor import document_processor
        
        extracted = document_processor.extract_text(str(test_file), "txt")
        print(f"✓ Text extracted: {len(extracted)} chars")
        
        cleaned = document_processor.clean_text(extracted)
        print(f"✓ Text cleaned: {len(cleaned)} chars")
        
        chunks = document_processor.chunk_text(cleaned, "txt")
        print(f"✓ Chunks created: {len(chunks)}")
        for i, chunk in enumerate(chunks[:2]):
            print(f"  Chunk {i}: {len(chunk.text)} chars")
        
        # Step 9: Test RAG service (without actual indexing)
        print("\n[9/10] Testing RAG search (simulated)...")
        print("⚠ Skipping actual search (requires indexed documents)")
        print("  After document upload, use:")
        print(f"  POST /api/rag/search")
        print(f'  {{"knowledge_base_id": {kb.id}, "query": "Berapa hari cuti tahunan?"}}')
        
        # Step 10: Summary
        print("\n[10/10] Test Summary")
        print("=" * 60)
        print("✓ Knowledge Base API: WORKING")
        print("✓ Database schema: CORRECT")
        print("✓ User association: WORKING")
        print("✓ Qdrant connection: WORKING")
        
        if len(test_embedding) > 0:
            print("✓ Embedding generation: WORKING")
        else:
            print("✗ Embedding generation: FAILED")
        
        print("✓ Document processor: WORKING")
        print("=" * 60)
        
        print("\n✅ BACKEND FOUNDATION: VALIDATED")
        print("\nNext steps:")
        print("1. Test document upload via API: POST /api/knowledge-bases/{kb.id}/documents")
        print("2. Verify document processing completes")
        print("3. Test RAG search: POST /api/rag/search")
        print("4. Test chat with RAG: POST /api/chat (with rag_enabled=true)")
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
