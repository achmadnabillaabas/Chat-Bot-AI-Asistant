"""
Chat API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
import httpx
import logging
from typing import List
import time

from app.core.database import get_db
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    MessageResponse,
    TokenUsageResponse,
    SourceInfo
)
from app.models.conversation import Conversation, Message
from app.models.token_usage import TokenUsage
from app.models.user import User
from app.models.knowledge_base import KnowledgeBase
from app.services.ninerouter_service import ninerouter_service
from app.services.rag_service import rag_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


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


@router.post("", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def create_chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    Send a chat message and get AI response.
    
    Flow:
    1. Get or create conversation
    2. Save user message
    3. Load conversation history
    4. Call 9Router
    5. Save assistant message
    6. Save token usage
    7. Return response
    """
    start_time = time.time()
    
    # Validate message
    if not request.message or not request.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message cannot be empty"
        )
    
    # Get default user (Phase 2 - no auth yet)
    user = get_default_user(db)
    
    try:
        # Get or create conversation
        if request.conversation_id:
            conversation = db.query(Conversation).filter(
                Conversation.id == request.conversation_id,
                Conversation.user_id == user.id
            ).first()
            
            if not conversation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found"
                )
        else:
            # Create new conversation
            # Use first few words of message as title
            title_words = request.message.split()[:5]
            title = " ".join(title_words)
            if len(title_words) >= 5:
                title += "..."
            
            conversation = Conversation(
                user_id=user.id,
                title=title
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
            
            logger.info(f"Created new conversation | id={conversation.id} | title={title}")
        
        # Save user message
        user_message = Message(
            conversation_id=conversation.id,
            role="user",
            content=request.message.strip()
        )
        db.add(user_message)
        db.commit()
        db.refresh(user_message)
        
        logger.info(f"Saved user message | conversation_id={conversation.id} | message_id={user_message.id}")
        
        # Load conversation history (last 10 messages for context)
        previous_messages = db.query(Message).filter(
            Message.conversation_id == conversation.id,
            Message.id < user_message.id
        ).order_by(Message.created_at.desc()).limit(10).all()
        
        previous_messages.reverse()  # Chronological order
        
        # Build messages for 9Router
        messages_for_ai = []
        for msg in previous_messages:
            messages_for_ai.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Add current user message
        messages_for_ai.append({
            "role": "user",
            "content": request.message.strip()
        })
        
        # RAG retrieval if enabled
        rag_sources = None
        if request.rag_enabled and request.knowledge_base_id:
            logger.info(f"RAG enabled | kb_id={request.knowledge_base_id}")
            
            # Verify KB ownership
            kb = db.query(KnowledgeBase).filter(
                KnowledgeBase.id == request.knowledge_base_id,
                KnowledgeBase.user_id == user.id
            ).first()
            
            if kb:
                # Perform RAG search
                retrieval_results = await rag_service.search(
                    query=request.message,
                    knowledge_base_id=request.knowledge_base_id,
                    db=db,
                    top_k=5
                )
                
                if retrieval_results:
                    # Build context from retrieved chunks
                    context = rag_service.build_context(retrieval_results)
                    
                    # Inject context into system message
                    system_message = {
                        "role": "system",
                        "content": f"""You are a helpful AI assistant with access to a knowledge base.

Use the retrieved context below to answer questions accurately.
If the answer is not in the context, state that clearly.

{context}"""
                    }
                    
                    # Insert system message at beginning
                    messages_for_ai.insert(0, system_message)
                    
                    # Extract sources
                    rag_sources = rag_service.get_sources(retrieval_results)
                    
                    logger.info(f"RAG context added | chunks={len(retrieval_results)} | sources={len(rag_sources)}")
            else:
                logger.warning(f"Knowledge base {request.knowledge_base_id} not found or unauthorized")
        
        # Call 9Router
        logger.info(f"Calling 9Router | combo={request.model or 'default'} | context_messages={len(messages_for_ai)}")
        
        try:
            ai_response = await ninerouter_service.chat_completion(
                messages=messages_for_ai,
                model=request.model
            )
        except httpx.HTTPStatusError as e:
            status_code = e.response.status_code
            
            # Parse error details
            error_detail = "AI service error"
            try:
                error_body = e.response.json()
                error_detail = error_body.get("error", {}).get("message", str(error_body))
            except:
                error_detail = str(e)
            
            logger.error(
                f"9Router HTTP error | "
                f"status={status_code} | "
                f"combo={request.model} | "
                f"detail={error_detail}"
            )
            
            # Return appropriate error based on status
            if status_code == 401:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="AI service authentication failed. Please contact administrator."
                )
            elif status_code == 400:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid request: {error_detail}"
                )
            elif status_code == 404:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"AI Combo '{request.model}' not found. Please select a valid combo."
                )
            elif status_code == 429:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded. Please try again in a moment."
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"AI service error ({status_code}). Please try again."
                )
                
        except httpx.TimeoutException:
            logger.error(f"9Router timeout | combo={request.model}")
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="AI service timeout. Please try again."
            )
            
        except httpx.RequestError as e:
            logger.error(f"9Router connection error | {type(e).__name__} | {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Cannot connect to AI service. Please try again."
            )
            
        except Exception as e:
            logger.error(f"Unexpected error calling 9Router: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred. Please try again."
            )
        
        # Save assistant message
        assistant_message = Message(
            conversation_id=conversation.id,
            role="assistant",
            content=ai_response["content"],
            model=ai_response["model"]
        )
        db.add(assistant_message)
        db.commit()
        db.refresh(assistant_message)
        
        logger.info(f"Saved assistant message | message_id={assistant_message.id}")
        
        # Calculate latency
        latency_ms = int((time.time() - start_time) * 1000)
        
        # Save token usage
        kb_id_to_save = request.knowledge_base_id if request.rag_enabled else None
        
        logger.info(
            f"Creating token usage record | "
            f"rag_enabled={request.rag_enabled} | "
            f"request.knowledge_base_id={request.knowledge_base_id} | "
            f"kb_id_to_save={kb_id_to_save}"
        )
        
        token_usage = TokenUsage(
            user_id=user.id,
            conversation_id=conversation.id,
            message_id=assistant_message.id,
            model=ai_response["model"],
            input_tokens=ai_response["usage"]["input_tokens"],
            output_tokens=ai_response["usage"]["output_tokens"],
            total_tokens=ai_response["usage"]["total_tokens"],
            request_type="chat",
            rag_enabled=1 if request.rag_enabled else 0,
            knowledge_base_id=kb_id_to_save,
            latency_ms=latency_ms
        )
        db.add(token_usage)
        db.commit()
        db.refresh(token_usage)
        
        logger.info(
            f"Saved token usage | "
            f"id={token_usage.id} | "
            f"rag_enabled={token_usage.rag_enabled} | "
            f"knowledge_base_id={token_usage.knowledge_base_id} | "
            f"input={token_usage.input_tokens} | "
            f"output={token_usage.output_tokens} | "
            f"total={token_usage.total_tokens} | "
            f"latency={latency_ms}ms"
        )
        
        # Update conversation timestamp
        conversation.updated_at = func.now()
        db.commit()
        
        # Build response
        sources_response = None
        if rag_sources:
            sources_response = [
                SourceInfo(
                    document_id=s["document_id"],
                    document_name=s["document_name"],
                    pages=s.get("pages")
                )
                for s in rag_sources
            ]
        
        return ChatResponse(
            conversation_id=conversation.id,
            message=MessageResponse(
                id=assistant_message.id,
                role=assistant_message.role,
                content=assistant_message.content,
                model=assistant_message.model,
                created_at=assistant_message.created_at
            ),
            usage=TokenUsageResponse(
                input_tokens=token_usage.input_tokens,
                output_tokens=token_usage.output_tokens,
                total_tokens=token_usage.total_tokens
            ),
            model=ai_response["model"],
            sources=sources_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat request failed: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred processing your request"
        )
