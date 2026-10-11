"""
RAG (Retrieval-Augmented Generation) service.
Handles document retrieval and context building for chat.
"""
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.services.embedding_service import embedding_service
from app.services.qdrant_service import qdrant_service
from app.models.knowledge_base import KnowledgeBase, Document

logger = logging.getLogger(__name__)


class RetrievalResult:
    """Represents a retrieved document chunk."""
    
    def __init__(
        self,
        document_id: int,
        document_name: str,
        chunk_id: int,
        page_number: Optional[int],
        text: str,
        score: float
    ):
        self.document_id = document_id
        self.document_name = document_name
        self.chunk_id = chunk_id
        self.page_number = page_number
        self.text = text
        self.score = score
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "document_id": self.document_id,
            "document_name": self.document_name,
            "chunk_id": self.chunk_id,
            "page_number": self.page_number,
            "text": self.text,
            "score": round(self.score, 4)
        }


class RAGService:
    """Service for RAG operations."""
    
    def __init__(self):
        self.embedding_service = embedding_service
        self.qdrant_service = qdrant_service
    
    async def search(
        self,
        query: str,
        knowledge_base_id: int,
        db: Session,
        top_k: int = 5,
        score_threshold: float = 0.3  # Lowered from 0.5 - multilingual embeddings have lower similarity scores
    ) -> List[RetrievalResult]:
        """
        Search for relevant document chunks.
        
        Args:
            query: User query
            knowledge_base_id: Knowledge base to search in
            db: Database session
            top_k: Number of results to return
            score_threshold: Minimum similarity score
            
        Returns:
            List of RetrievalResult objects
        """
        try:
            # Get knowledge base
            kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == knowledge_base_id).first()
            if not kb:
                logger.error(f"Knowledge base {knowledge_base_id} not found")
                return []
            
            collection_name = kb.collection_name
            
            # Check if collection exists
            if not self.qdrant_service.collection_exists(collection_name):
                logger.warning(f"Collection {collection_name} does not exist")
                return []
            
            # Generate query embedding
            query_vector = await self.embedding_service.generate_embedding(query)
            
            if not query_vector:
                logger.error("Failed to generate query embedding")
                return []
            
            # Search in Qdrant
            results = self.qdrant_service.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=top_k,
                filters={"knowledge_base_id": knowledge_base_id},
                score_threshold=score_threshold
            )
            
            # Format results
            retrieval_results = []
            for result in results:
                payload = result["payload"]
                retrieval_results.append(RetrievalResult(
                    document_id=payload.get("document_id"),
                    document_name=payload.get("document_name", "Unknown"),
                    chunk_id=payload.get("chunk_index", 0),
                    page_number=payload.get("page_number"),
                    text=payload.get("text", ""),
                    score=result["score"]
                ))
            
            logger.info(f"Retrieved {len(retrieval_results)} chunks for query from KB {knowledge_base_id}")
            return retrieval_results
            
        except Exception as e:
            logger.error(f"Error in RAG search: {str(e)}")
            return []
    
    def build_context(self, results: List[RetrievalResult]) -> str:
        """
        Build context string from retrieval results.
        
        Args:
            results: List of retrieval results
            
        Returns:
            Formatted context string
        """
        if not results:
            return ""
        
        context_parts = []
        context_parts.append("Retrieved context from knowledge base:")
        context_parts.append("")
        
        for i, result in enumerate(results, 1):
            source_info = f"[Source: {result.document_name}"
            if result.page_number:
                source_info += f", Page {result.page_number}"
            source_info += f"]"
            
            context_parts.append(f"{i}. {source_info}")
            context_parts.append(result.text)
            context_parts.append("")
        
        return "\n".join(context_parts)
    
    def get_sources(self, results: List[RetrievalResult]) -> List[Dict[str, Any]]:
        """
        Extract source information from results.
        
        Args:
            results: List of retrieval results
            
        Returns:
            List of source dictionaries
        """
        # Group by document
        sources_map = {}
        
        for result in results:
            doc_key = result.document_id
            if doc_key not in sources_map:
                sources_map[doc_key] = {
                    "document_id": result.document_id,
                    "document_name": result.document_name,
                    "pages": set()
                }
            
            if result.page_number:
                sources_map[doc_key]["pages"].add(result.page_number)
        
        # Format sources
        sources = []
        for source in sources_map.values():
            source_info = {
                "document_id": source["document_id"],
                "document_name": source["document_name"]
            }
            
            if source["pages"]:
                pages = sorted(list(source["pages"]))
                source_info["pages"] = pages
            
            sources.append(source_info)
        
        return sources


# Singleton instance
rag_service = RAGService()
