"""Test embedding generation."""
import asyncio
from app.services.embedding_service import embedding_service

async def test():
    print("Testing embedding generation...")
    
    # Test single embedding
    print("\n1. Generating single embedding...")
    try:
        embedding = await embedding_service.generate_embedding("test query")
        print(f"✓ Embedding generated")
        print(f"  Dimension: {len(embedding)}")
        print(f"  First 5 values: {embedding[:5]}")
    except Exception as e:
        print(f"X Failed: {type(e).__name__}: {str(e)}")
        print("\n9Router does NOT support embeddings.")
        print("Need to implement alternative provider.")
        return False
    
    # Test batch embeddings
    print("\n2. Generating batch embeddings...")
    try:
        embeddings = await embedding_service.generate_embeddings([
            "first text",
            "second text",
            "third text"
        ])
        print(f"✓ Batch generated: {len(embeddings)} embeddings")
    except Exception as e:
        print(f"X Failed: {e}")
        return False
    
    print("\nOK Embedding service: WORKING")
    print(f"Provider: sentence-transformers (LOCAL)")
    print(f"Model: {embedding_service.model_name}")
    print(f"Dimension: {embedding_service.get_embedding_dimension()}")
    return True

if __name__ == "__main__":
    success = asyncio.run(test())
    exit(0 if success else 1)
