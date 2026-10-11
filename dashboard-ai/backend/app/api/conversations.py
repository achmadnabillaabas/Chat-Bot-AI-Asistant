"""
Conversations API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
import logging

from app.core.database import get_db
from app.schemas.chat import ConversationListItem, ConversationDetail, MessageResponse
from app.models.conversation import Conversation, Message
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/conversations", tags=["conversations"])


def get_default_user(db: Session) -> User:
    """
    Get or create default user for Phase 2.
    In Phase 9, this will be replaced with proper authentication.
    """
    user = db.query(User).filter(User.email == "demo@aiassistant.local").first()
    if not user:
        user = User(
            email="demo@aiassistant.local",
            username="demo_user",
            hashed_password="demo",  # Not used in Phase 2
            full_name="Demo User",
            role="user",
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


@router.get("", response_model=List[ConversationListItem])
async def list_conversations(
    limit: int = 50,
    offset: int = 0,
    search: str = None,
    db: Session = Depends(get_db)
):
    """
    List user's conversations ordered by most recent.
    Supports optional search by title.
    """
    try:
        logger.info("Attempting to get default user")
        user = get_default_user(db)
        logger.info(f"Got user | id={user.id} | email={user.email}")
        
        # Query conversations with message count
        logger.info(f"Querying conversations for user_id={user.id}, search={search}")
        query = db.query(
            Conversation,
            func.count(Message.id).label("message_count")
        ).outerjoin(
            Message, Conversation.id == Message.conversation_id
        ).filter(
            Conversation.user_id == user.id
        )
        
        # Apply search filter if provided
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(Conversation.title.ilike(search_pattern))
        
        conversations = query.group_by(
            Conversation.id
        ).order_by(
            Conversation.updated_at.desc()
        ).limit(limit).offset(offset).all()
        
        logger.info(f"Query returned {len(conversations)} conversations")
        
        result = []
        for conv, msg_count in conversations:
            result.append(ConversationListItem(
                id=conv.id,
                title=conv.title,
                created_at=conv.created_at,
                updated_at=conv.updated_at,
                message_count=msg_count
            ))
        
        logger.info(f"Successfully retrieved {len(result)} conversations for user {user.id}")
        return result
        
    except HTTPException:
        # Re-raise HTTP exceptions (like 404)
        raise
    except Exception as e:
        # Log full exception with traceback
        logger.exception(f"Failed to list conversations: {type(e).__name__}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve conversations: {type(e).__name__}"
        )


@router.get("/{conversation_id}", response_model=ConversationDetail)
async def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    """
    Get conversation details with all messages.
    """
    user = get_default_user(db)
    
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == user.id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Load messages
    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at).all()
    
    return ConversationDetail(
        id=conversation.id,
        title=conversation.title,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        messages=[MessageResponse(
            id=msg.id,
            role=msg.role,
            content=msg.content,
            model=msg.model,
            created_at=msg.created_at
        ) for msg in messages]
    )


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a conversation and all its messages.
    """
    user = get_default_user(db)
    
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == user.id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    db.delete(conversation)
    db.commit()
    
    logger.info(f"Deleted conversation | id={conversation_id}")
