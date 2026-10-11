"""
Debug RAG retrieval - find why search returns 0 results.
"""
import asyncio
from app.core.database import SessionLocal
from app.models.knowledge_base import KnowledgeBase, Document, DocumentChunk
from app.services.embedding_service import embedding_service
from app.services.qdrant_service import qdrant_service

print("=" * 70)
print("RAG RETRIEVAL DEBUG")
print("=" * 70)

async def debug():
    db = SessionLocal()
    
    try:
        # Step 1: Find the test KB
        print("\n[1] Finding Test RAG Knowledge Base...")
        kb = db.query(KnowledgeBase).filter(KnowledgeBase.name == "Test RAG Debug").first()
        if not kb:
            print("X Test RAG KB not found. Create it first.")
            return
        
        print(f"OK Found KB: id={kb.id}, collection={kb.collection_name}")
        
        # Step 2: Check documents
        print("\n[2] Checking documents...")
        docs = db.query(Document).filter(Document.knowledge_base_id == kb.id).all()
        print(f"OK Found {len(docs)} documents")
        
        if not docs:
            print("X No documents in KB")
            return
        
        for doc in docs:
            print(f"   - {doc.filename}: status={doc.status}, chunks={doc.chunk_count}")
        
        # Step 3: Check chunks in database
        print("\n[3] Checking document chunks in PostgreSQL...")
        chunks = db.query(DocumentChunk).join(Document).filter(
            Document.knowledge_base_id == kb.id
        ).all()
        print(f"OK Found {len(chunks)} chunks in database")
        
        if not chunks:
            print("X No chunks in database")
            return
        
        for chunk in chunks[:3]:  # Show first 3
            print(f"   Chunk {chunk.chunk_index}:")
            print(f"      Text: {chunk.content[:100]}...")
            print(f"      Vector ID: {chunk.vector_id}")
        
        # Step 4: Check Qdrant collection
        print("\n[4] Checking Qdrant collection...")
        collection_name = kb.collection_name
        
        if not qdrant_service.collection_exists(collection_name):
            print(f"X Collection {collection_name} does NOT exist in Qdrant!")
            return
        
        print(f"OK Collection exists: {collection_name}")
        
        # Get collection info
        try:
            collection_info = qdrant_service.client.get_collection(collection_name)
            print(f"   Points count: {collection_info.points_count}")
            print(f"   Vector size: {collection_info.config.params.vectors.size}")
        except Exception as e:
            print(f"   Error getting collection info: {e}")
        
        # Step 5: Test query embedding
        print("\n[5] Generating query embedding...")
        query = "Berapa hari cuti tahunan?"
        query_embedding = await embedding_service.generate_embedding(query)
        
        print(f"OK Query embedding generated")
        print(f"   Dimension: {len(query_embedding)}")
        print(f"   First 5 values: {query_embedding[:5]}")
        
        # Step 6: Direct Qdrant search WITHOUT filter
        print("\n[6] Direct Qdrant search (NO score threshold, NO filter)...")
        try:
            raw_results = qdrant_service.client.search(
                collection_name=collection_name,
                query_vector=query_embedding,
                limit=5
            )
            
            print(f"OK Retrieved {len(raw_results)} points (unfiltered)")
            for i, result in enumerate(raw_results):
                print(f"   Result {i+1}:")
                print(f"      Score: {result.score}")
                print(f"      KB ID: {result.payload.get('knowledge_base_id')}")
                print(f"      Doc: {result.payload.get('document_name')}")
                print(f"      Text: {result.payload.get('text', '')[:80]}...")
        except Exception as e:
            print(f"X Qdrant search failed: {e}")
            return
        
        # Step 7: Qdrant search WITH filter but NO threshold
        print("\n[7] Qdrant search (WITH KB filter, NO threshold)...")
        try:
            from qdrant_client.models import Filter, FieldCondition, MatchValue
            
            query_filter = Filter(
                must=[
                    FieldCondition(
                        key="knowledge_base_id",
                        match=MatchValue(value=kb.id)
                    )
                ]
            )
            
            filtered_results = qdrant_service.client.search(
                collection_name=collection_name,
                query_vector=query_embedding,
                limit=5,
                query_filter=query_filter
            )
            
            print(f"OK Retrieved {len(filtered_results)} points (with KB filter)")
            for i, result in enumerate(filtered_results):
                print(f"   Result {i+1}:")
                print(f"      Score: {result.score}")
                print(f"      KB ID: {result.payload.get('knowledge_base_id')} (filter: {kb.id})")
                print(f"      Doc: {result.payload.get('document_name')}")
                print(f"      Text: {result.payload.get('text', '')[:80]}...")
        except Exception as e:
            print(f"X Filtered search failed: {e}")
        
        # Step 8: Qdrant search WITH filter AND threshold=0.5
        print("\n[8] Qdrant search (WITH KB filter, threshold=0.5)...")
        try:
            threshold_results = qdrant_service.client.search(
                collection_name=collection_name,
                query_vector=query_embedding,
                limit=5,
                query_filter=query_filter,
                score_threshold=0.5
            )
            
            print(f"OK Retrieved {len(threshold_results)} points (threshold=0.5)")
            if not threshold_results:
                print("   ^ THIS IS THE PROBLEM!")
                print("   Scores are below 0.5 threshold")
        except Exception as e:
            print(f"X Threshold search failed: {e}")
        
        # Step 9: Qdrant search WITH filter AND threshold=0.3
        print("\n[9] Qdrant search (WITH KB filter, threshold=0.3)...")
        try:
            lower_threshold_results = qdrant_service.client.search(
                collection_name=collection_name,
                query_vector=query_embedding,
                limit=5,
                query_filter=query_filter,
                score_threshold=0.3
            )
            
            print(f"OK Retrieved {len(lower_threshold_results)} points (threshold=0.3)")
            for i, result in enumerate(lower_threshold_results):
                print(f"   Result {i+1}:")
                print(f"      Score: {result.score}")
        except Exception as e:
            print(f"X Lower threshold search failed: {e}")
        
        print("\n" + "=" * 70)
        print("DEBUG COMPLETE")
        print("=" * 70)
        
        # Diagnosis
        print("\nDIAGNOSIS:")
        if len(raw_results) > 0 and len(filtered_results) == 0:
            print("ISSUE: KB filter is removing all results")
            print("CHECK: knowledge_base_id type mismatch or value mismatch")
        elif len(filtered_results) > 0 and len(threshold_results) == 0:
            print("ISSUE: Score threshold 0.5 is too high")
            print("SOLUTION: Lower default threshold to 0.3 or make configurable")
            print(f"Max score found: {max(r.score for r in filtered_results)}")
        elif len(raw_results) == 0:
            print("ISSUE: No vectors in Qdrant collection")
            print("CHECK: Document processing/indexing failed")
        else:
            print("OK: All searches working")
        
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(debug())
