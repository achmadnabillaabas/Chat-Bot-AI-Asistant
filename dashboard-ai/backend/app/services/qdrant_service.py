"""
Qdrant vector database service.
Handles collection management, vector storage, and similarity search.
"""
import logging
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue
)
from app.core.config import settings

logger = logging.getLogger(__name__)


class QdrantService:
    """Service for interacting with Qdrant vector database."""
    
    def __init__(self):
        self.client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY if settings.QDRANT_API_KEY != "your_qdrant_api_key" else None
        )
        # Get actual dimension from embedding service
        from app.services.embedding_service import embedding_service
        self.default_dimension = embedding_service.get_embedding_dimension()
    
    def create_collection(self, collection_name: str, dimension: int = None) -> bool:
        """
        Create a new Qdrant collection.
        
        Args:
            collection_name: Name of the collection
            dimension: Vector dimension (default: 1536)
            
        Returns:
            True if successful
        """
        try:
            if dimension is None:
                dimension = self.default_dimension
            
            # Check if collection already exists
            collections = self.client.get_collections().collections
            if any(c.name == collection_name for c in collections):
                logger.info(f"Collection {collection_name} already exists")
                return True
            
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=dimension,
                    distance=Distance.COSINE
                )
            )
            logger.info(f"Created collection: {collection_name} with dimension {dimension}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating collection {collection_name}: {str(e)}")
            raise
    
    def delete_collection(self, collection_name: str) -> bool:
        """
        Delete a Qdrant collection.
        
        Args:
            collection_name: Name of the collection to delete
            
        Returns:
            True if successful
        """
        try:
            self.client.delete_collection(collection_name=collection_name)
            logger.info(f"Deleted collection: {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Error deleting collection {collection_name}: {str(e)}")
            raise
    
    def upsert_vectors(
        self,
        collection_name: str,
        vectors: List[List[float]],
        payloads: List[Dict[str, Any]],
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """
        Insert or update vectors in a collection.
        
        Args:
            collection_name: Target collection
            vectors: List of embedding vectors
            payloads: List of metadata dictionaries
            ids: Optional list of IDs (will be generated if not provided)
            
        Returns:
            List of point IDs
        """
        try:
            if not vectors or not payloads:
                return []
            
            if len(vectors) != len(payloads):
                raise ValueError("Vectors and payloads must have the same length")
            
            # Generate IDs if not provided
            if ids is None:
                import uuid
                ids = [str(uuid.uuid4()) for _ in range(len(vectors))]
            
            # Create points
            points = [
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=payload
                )
                for point_id, vector, payload in zip(ids, vectors, payloads)
            ]
            
            # Upsert points
            self.client.upsert(
                collection_name=collection_name,
                points=points
            )
            
            logger.info(f"Upserted {len(points)} vectors to {collection_name}")
            return ids
            
        except Exception as e:
            logger.error(f"Error upserting vectors to {collection_name}: {str(e)}")
            raise
    
    def search(
        self,
        collection_name: str,
        query_vector: List[float],
        limit: int = 5,
        filters: Optional[Dict[str, Any]] = None,
        score_threshold: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors in a collection.
        
        Args:
            collection_name: Collection to search
            query_vector: Query embedding vector
            limit: Maximum number of results
            filters: Optional metadata filters (e.g., {"knowledge_base_id": 1})
            score_threshold: Minimum similarity score
            
        Returns:
            List of search results with scores and payloads
        """
        try:
            # Build filter conditions
            query_filter = None
            if filters:
                conditions = []
                for key, value in filters.items():
                    conditions.append(
                        FieldCondition(
                            key=key,
                            match=MatchValue(value=value)
                        )
                    )
                query_filter = Filter(must=conditions)
            
            # Perform search
            results = self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=limit,
                query_filter=query_filter,
                score_threshold=score_threshold
            )
            
            # Format results
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "id": result.id,
                    "score": result.score,
                    "payload": result.payload
                })
            
            logger.info(f"Found {len(formatted_results)} results in {collection_name}")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching in {collection_name}: {str(e)}")
            raise
    
    def delete_vectors(
        self,
        collection_name: str,
        filters: Dict[str, Any]
    ) -> bool:
        """
        Delete vectors matching filters.
        
        Args:
            collection_name: Collection name
            filters: Metadata filters (e.g., {"document_id": 5})
            
        Returns:
            True if successful
        """
        try:
            conditions = []
            for key, value in filters.items():
                conditions.append(
                    FieldCondition(
                        key=key,
                        match=MatchValue(value=value)
                    )
                )
            
            self.client.delete(
                collection_name=collection_name,
                points_selector=Filter(must=conditions)
            )
            
            logger.info(f"Deleted vectors from {collection_name} with filters: {filters}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting vectors from {collection_name}: {str(e)}")
            raise
    
    def collection_exists(self, collection_name: str) -> bool:
        """
        Check if a collection exists.
        
        Args:
            collection_name: Collection name to check
            
        Returns:
            True if collection exists
        """
        try:
            collections = self.client.get_collections().collections
            return any(c.name == collection_name for c in collections)
        except Exception as e:
            logger.error(f"Error checking collection {collection_name}: {str(e)}")
            return False


# Singleton instance
qdrant_service = QdrantService()
