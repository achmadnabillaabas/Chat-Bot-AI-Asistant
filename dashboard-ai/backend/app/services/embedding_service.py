"""
Embedding service for generating vector embeddings.
Uses sentence-transformers for local embedding generation.
"""
import logging
from typing import List
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating text embeddings using sentence-transformers."""
    
    def __init__(self):
        # Use a lightweight multilingual model
        # all-MiniLM-L6-v2: English, 384 dimensions, fast
        # paraphrase-multilingual-MiniLM-L12-v2: Multilingual including Indonesian, 384 dimensions
        self.model_name = "paraphrase-multilingual-MiniLM-L12-v2"
        logger.info(f"Loading embedding model: {self.model_name}")
        self.model = SentenceTransformer(self.model_name)
        logger.info(f"Embedding model loaded: dimension={self.model.get_embedding_dimension()}")
        
    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        embeddings = await self.generate_embeddings([text])
        return embeddings[0] if embeddings else []
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batch.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
            
        try:
            # Generate embeddings (synchronous operation wrapped in async)
            embeddings = self.model.encode(
                texts,
                convert_to_tensor=False,
                show_progress_bar=False
            )
            
            # Convert to list of lists
            result = embeddings.tolist()
            
            logger.info(f"Generated {len(result)} embeddings")
            return result
                
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise
    
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of embeddings produced by the model.
        
        Returns:
            Embedding dimension
        """
        return self.model.get_embedding_dimension()


# Singleton instance
embedding_service = EmbeddingService()
