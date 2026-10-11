"""
Knowledge Base API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
import logging
import uuid

from app.core.database import get_db
from app.schemas.knowledge_base import (
    KnowledgeBaseCreate,
    KnowledgeBaseUpdate,
    KnowledgeBaseResponse,
    KnowledgeBaseListResponse
)
from app.models.knowledge_base import KnowledgeBase, Document
from app.models.user import User
from app.services.qdrant_service import qdrant_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/knowledge-bases", tags=["knowledge-bases"])


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


@router.get("", response_model=KnowledgeBaseListResponse)
async def list_knowledge_bases(
    db: Session = Depends(get_db)
):
    """
    List all knowledge bases for the current user.
    """
    user = get_default_user(db)
    
    # Query with document count
    kbs = db.query(
        KnowledgeBase,
        func.count(Document.id).label("document_count")
    ).outerjoin(
        Document, KnowledgeBase.id == Document.knowledge_base_id
    ).filter(
        KnowledgeBase.user_id == user.id
    ).group_by(
        KnowledgeBase.id
    ).order_by(
        KnowledgeBase.created_at.desc()
    ).all()
    
    items = []
    for kb, doc_count in kbs:
        items.append(KnowledgeBaseResponse(
            id=kb.id,
            name=kb.name,
            description=kb.description,
            collection_name=kb.collection_name,
            document_count=doc_count,
            created_at=kb.created_at,
            updated_at=kb.updated_at
        ))
    
    return KnowledgeBaseListResponse(
        items=items,
        total=len(items)
    )


@router.post("", response_model=KnowledgeBaseResponse, status_code=status.HTTP_201_CREATED)
async def create_knowledge_base(
    request: KnowledgeBaseCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new knowledge base.
    """
    user = get_default_user(db)
    
    # Generate unique collection name
    collection_name = f"kb_{uuid.uuid4().hex[:16]}"
    
    # Create knowledge base
    kb = KnowledgeBase(
        user_id=user.id,
        name=request.name.strip(),
        description=request.description.strip() if request.description else None,
        collection_name=collection_name
    )
    db.add(kb)
    db.commit()
    db.refresh(kb)
    
    # Create Qdrant collection
    try:
        qdrant_service.create_collection(collection_name)
    except Exception as e:
        logger.error(f"Failed to create Qdrant collection: {str(e)}")
        db.delete(kb)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initialize knowledge base storage"
        )
    
    logger.info(f"Created knowledge base | id={kb.id} | name={kb.name}")
    
    return KnowledgeBaseResponse(
        id=kb.id,
        name=kb.name,
        description=kb.description,
        collection_name=kb.collection_name,
        document_count=0,
        created_at=kb.created_at,
        updated_at=kb.updated_at
    )


@router.get("/{kb_id}", response_model=KnowledgeBaseResponse)
async def get_knowledge_base(
    kb_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific knowledge base.
    """
    user = get_default_user(db)
    
    kb = db.query(KnowledgeBase).filter(
        KnowledgeBase.id == kb_id,
        KnowledgeBase.user_id == user.id
    ).first()
    
    if not kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge base not found"
        )
    
    # Get document count
    doc_count = db.query(func.count(Document.id)).filter(
        Document.knowledge_base_id == kb_id
    ).scalar()
    
    return KnowledgeBaseResponse(
        id=kb.id,
        name=kb.name,
        description=kb.description,
        collection_name=kb.collection_name,
        document_count=doc_count,
        created_at=kb.created_at,
        updated_at=kb.updated_at
    )


@router.patch("/{kb_id}", response_model=KnowledgeBaseResponse)
async def update_knowledge_base(
    kb_id: int,
    request: KnowledgeBaseUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a knowledge base.
    """
    user = get_default_user(db)
    
    kb = db.query(KnowledgeBase).filter(
        KnowledgeBase.id == kb_id,
        KnowledgeBase.user_id == user.id
    ).first()
    
    if not kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge base not found"
        )
    
    # Update fields
    if request.name is not None:
        kb.name = request.name.strip()
    if request.description is not None:
        kb.description = request.description.strip() if request.description else None
    
    kb.updated_at = func.now()
    db.commit()
    db.refresh(kb)
    
    # Get document count
    doc_count = db.query(func.count(Document.id)).filter(
        Document.knowledge_base_id == kb_id
    ).scalar()
    
    logger.info(f"Updated knowledge base | id={kb.id}")
    
    return KnowledgeBaseResponse(
        id=kb.id,
        name=kb.name,
        description=kb.description,
        collection_name=kb.collection_name,
        document_count=doc_count,
        created_at=kb.created_at,
        updated_at=kb.updated_at
    )


@router.delete("/{kb_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_knowledge_base(
    kb_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a knowledge base and all its documents.
    """
    user = get_default_user(db)
    
    kb = db.query(KnowledgeBase).filter(
        KnowledgeBase.id == kb_id,
        KnowledgeBase.user_id == user.id
    ).first()
    
    if not kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge base not found"
        )
    
    collection_name = kb.collection_name
    
    # Delete from database (cascades to documents and chunks)
    db.delete(kb)
    db.commit()
    
    # Delete Qdrant collection
    try:
        if qdrant_service.collection_exists(collection_name):
            qdrant_service.delete_collection(collection_name)
    except Exception as e:
        logger.error(f"Failed to delete Qdrant collection {collection_name}: {str(e)}")
    
    logger.info(f"Deleted knowledge base | id={kb_id}")
    
    return None
