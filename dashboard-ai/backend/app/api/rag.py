"""
RAG Search API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.schemas.rag import RAGSearchRequest, RAGSearchResponse, RAGResultItem, RAGSourceResponse
from app.models.knowledge_base import KnowledgeBase
from app.models.user import User
from app.services.rag_service import rag_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/rag", tags=["rag"])


def get_default_user(db: Session) -> User:
    """Get default user."""
    user = db.query(User).filter(User.email == "demo@aiassistant.local").first()
    if not user:
        user = User(
            email="demo@aiassistant.local",
            username="demo_user",
            hashed_password="demo",
            full_name="Demo User",
            role="user",
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


@router.post("/search", response_model=RAGSearchResponse)
async def search_knowledge_base(
    request: RAGSearchRequest,
    db: Session = Depends(get_db)
):
    """
    Search for relevant information in a knowledge base.
    """
    user = get_default_user(db)
    
    # Check KB ownership
    kb = db.query(KnowledgeBase).filter(
        KnowledgeBase.id == request.knowledge_base_id,
        KnowledgeBase.user_id == user.id
    ).first()
    
    if not kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge base not found"
        )
    
    # Perform RAG search
    results = await rag_service.search(
        query=request.query,
        knowledge_base_id=request.knowledge_base_id,
        db=db,
        top_k=request.top_k
    )
    
    # Format results
    result_items = [
        RAGResultItem(
            document_id=r.document_id,
            document_name=r.document_name,
            chunk_id=r.chunk_id,
            page_number=r.page_number,
            text=r.text,
            score=r.score
        )
        for r in results
    ]
    
    # Get sources
    sources_data = rag_service.get_sources(results)
    sources = [
        RAGSourceResponse(
            document_id=s["document_id"],
            document_name=s["document_name"],
            pages=s.get("pages")
        )
        for s in sources_data
    ]
    
    return RAGSearchResponse(
        query=request.query,
        knowledge_base_id=request.knowledge_base_id,
        results=result_items,
        sources=sources
    )
