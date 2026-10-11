"""
Analytics API endpoints for token usage.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, case
from typing import List, Optional
from datetime import datetime, timedelta, date as date_type
import logging
import math

from app.core.database import get_db
from app.schemas.analytics import (
    UsageSummary,
    DailyUsage,
    ComboUsage,
    ConversationUsage,
    RequestDetail,
    RequestHistory
)
from app.models.token_usage import TokenUsage
from app.models.conversation import Conversation
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analytics", tags=["analytics"])


def get_default_user(db: Session) -> User:
    """Get default user for Phase 3 (same as other endpoints)."""
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


@router.get("/usage/summary", response_model=UsageSummary)
async def get_usage_summary(
    days: Optional[int] = Query(default=None, ge=1, le=365),
    start_date: Optional[date_type] = None,
    end_date: Optional[date_type] = None,
    combo: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get overall token usage summary.
    
    Aggregates all token usage for the workspace (includes Web + Telegram).
    Can filter by days (last N days) or explicit start_date/end_date.
    """
    # Build query - NO user_id filter to include all workspace users (Web + Telegram)
    query = db.query(
        func.count(TokenUsage.id).label("total_requests"),
        func.sum(TokenUsage.input_tokens).label("total_input_tokens"),
        func.sum(TokenUsage.output_tokens).label("total_output_tokens"),
        func.sum(TokenUsage.total_tokens).label("total_tokens")
    )
    
    # Apply date filters - prefer days parameter over explicit dates
    if days:
        end_date_calc = datetime.utcnow().date()
        start_date_calc = end_date_calc - timedelta(days=days - 1)
        query = query.filter(
            and_(
                func.date(TokenUsage.created_at) >= start_date_calc,
                func.date(TokenUsage.created_at) <= end_date_calc
            )
        )
    else:
        if start_date:
            query = query.filter(func.date(TokenUsage.created_at) >= start_date)
        if end_date:
            query = query.filter(func.date(TokenUsage.created_at) <= end_date)
    
    if combo:
        query = query.filter(TokenUsage.model == combo)
    
    result = query.first()
    
    logger.info(f"Analytics summary | requests={result.total_requests} | total_tokens={result.total_tokens}")
    
    return UsageSummary(
        total_requests=result.total_requests or 0,
        total_input_tokens=result.total_input_tokens or 0,
        total_output_tokens=result.total_output_tokens or 0,
        total_tokens=result.total_tokens or 0
    )


@router.get("/usage/timeseries", response_model=List[DailyUsage])
async def get_usage_timeseries(
    days: int = Query(default=7, ge=1, le=90),
    combo: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get daily token usage time series.
    
    Returns aggregated usage for the last N days (includes Web + Telegram).
    """
    # Calculate date range
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=days - 1)
    
    # Build query with date truncation - NO user_id filter
    query = db.query(
        func.date(TokenUsage.created_at).label("date"),
        func.sum(TokenUsage.input_tokens).label("input_tokens"),
        func.sum(TokenUsage.output_tokens).label("output_tokens"),
        func.sum(TokenUsage.total_tokens).label("total_tokens"),
        func.count(TokenUsage.id).label("requests")
    ).filter(
        and_(
            func.date(TokenUsage.created_at) >= start_date,
            func.date(TokenUsage.created_at) <= end_date
        )
    )
    
    # Apply combo filter
    if combo:
        query = query.filter(TokenUsage.model == combo)
    
    query = query.group_by(func.date(TokenUsage.created_at))
    query = query.order_by(func.date(TokenUsage.created_at))
    
    results = query.all()
    
    # Create complete date range with zeros for missing days
    date_map = {r.date: r for r in results}
    complete_series = []
    
    current_date = start_date
    while current_date <= end_date:
        if current_date in date_map:
            r = date_map[current_date]
            complete_series.append(DailyUsage(
                date=current_date,
                input_tokens=r.input_tokens or 0,
                output_tokens=r.output_tokens or 0,
                total_tokens=r.total_tokens or 0,
                requests=r.requests or 0
            ))
        else:
            complete_series.append(DailyUsage(
                date=current_date,
                input_tokens=0,
                output_tokens=0,
                total_tokens=0,
                requests=0
            ))
        current_date += timedelta(days=1)
    
    return complete_series


@router.get("/usage/by-combo", response_model=List[ComboUsage])
async def get_usage_by_combo(
    days: Optional[int] = Query(default=None, ge=1, le=365),
    start_date: Optional[date_type] = None,
    end_date: Optional[date_type] = None,
    db: Session = Depends(get_db)
):
    """
    Get token usage grouped by AI Combo.
    Can filter by days (last N days) or explicit start_date/end_date.
    Includes Web + Telegram usage.
    """
    # Build query - NO user_id filter
    query = db.query(
        TokenUsage.model.label("combo_id"),
        func.count(TokenUsage.id).label("requests"),
        func.sum(TokenUsage.input_tokens).label("input_tokens"),
        func.sum(TokenUsage.output_tokens).label("output_tokens"),
        func.sum(TokenUsage.total_tokens).label("total_tokens"),
        func.avg(TokenUsage.input_tokens).label("avg_input_tokens"),
        func.avg(TokenUsage.output_tokens).label("avg_output_tokens")
    )
    
    # Apply date filters - prefer days parameter over explicit dates
    if days:
        end_date_calc = datetime.utcnow().date()
        start_date_calc = end_date_calc - timedelta(days=days - 1)
        query = query.filter(
            and_(
                func.date(TokenUsage.created_at) >= start_date_calc,
                func.date(TokenUsage.created_at) <= end_date_calc
            )
        )
    else:
        if start_date:
            query = query.filter(func.date(TokenUsage.created_at) >= start_date)
        if end_date:
            query = query.filter(func.date(TokenUsage.created_at) <= end_date)
    
    query = query.group_by(TokenUsage.model)
    query = query.order_by(func.sum(TokenUsage.total_tokens).desc())
    
    results = query.all()
    
    return [
        ComboUsage(
            combo_id=r.combo_id,
            requests=r.requests or 0,
            input_tokens=r.input_tokens or 0,
            output_tokens=r.output_tokens or 0,
            total_tokens=r.total_tokens or 0,
            avg_input_tokens=round(r.avg_input_tokens or 0, 1),
            avg_output_tokens=round(r.avg_output_tokens or 0, 1)
        )
        for r in results
    ]


@router.get("/usage/by-conversation", response_model=List[ConversationUsage])
async def get_usage_by_conversation(
    days: Optional[int] = Query(default=None, ge=1, le=365),
    start_date: Optional[date_type] = None,
    end_date: Optional[date_type] = None,
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get token usage grouped by conversation.
    Can filter by days (last N days) or explicit start_date/end_date.
    Includes Web + Telegram conversations.
    """
    # Build query with conversation join - NO user_id filter to include Telegram
    query = db.query(
        TokenUsage.conversation_id.label("conversation_id"),
        Conversation.title.label("conversation_title"),
        func.count(TokenUsage.id).label("requests"),
        func.sum(TokenUsage.input_tokens).label("input_tokens"),
        func.sum(TokenUsage.output_tokens).label("output_tokens"),
        func.sum(TokenUsage.total_tokens).label("total_tokens")
    ).outerjoin(
        Conversation, TokenUsage.conversation_id == Conversation.id
    ).filter(
        TokenUsage.conversation_id.isnot(None)
    )
    
    # Apply date filters - prefer days parameter over explicit dates
    if days:
        end_date_calc = datetime.utcnow().date()
        start_date_calc = end_date_calc - timedelta(days=days - 1)
        query = query.filter(
            and_(
                func.date(TokenUsage.created_at) >= start_date_calc,
                func.date(TokenUsage.created_at) <= end_date_calc
            )
        )
    else:
        if start_date:
            query = query.filter(func.date(TokenUsage.created_at) >= start_date)
        if end_date:
            query = query.filter(func.date(TokenUsage.created_at) <= end_date)
    
    query = query.group_by(TokenUsage.conversation_id, Conversation.title)
    query = query.order_by(func.sum(TokenUsage.total_tokens).desc())
    query = query.limit(limit)
    
    results = query.all()
    
    return [
        ConversationUsage(
            conversation_id=r.conversation_id,
            conversation_title=r.conversation_title or f"Conversation {r.conversation_id}",
            requests=r.requests or 0,
            input_tokens=r.input_tokens or 0,
            output_tokens=r.output_tokens or 0,
            total_tokens=r.total_tokens or 0
        )
        for r in results
    ]


@router.get("/usage/requests", response_model=RequestHistory)
async def get_request_history(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=10, le=100),
    days: Optional[int] = Query(default=None, ge=1, le=365),
    start_date: Optional[date_type] = None,
    end_date: Optional[date_type] = None,
    combo: Optional[str] = None,
    conversation_id: Optional[int] = None,
    request_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get paginated request history with filters.
    Can filter by days (last N days) or explicit start_date/end_date.
    Includes Web + Telegram requests.
    """
    # Build base query - NO user_id filter to include Telegram
    query = db.query(TokenUsage, Conversation.title.label("conversation_title"))
    query = query.outerjoin(Conversation, TokenUsage.conversation_id == Conversation.id)
    
    # Apply date filters - prefer days parameter over explicit dates
    if days:
        end_date_calc = datetime.utcnow().date()
        start_date_calc = end_date_calc - timedelta(days=days - 1)
        query = query.filter(
            and_(
                func.date(TokenUsage.created_at) >= start_date_calc,
                func.date(TokenUsage.created_at) <= end_date_calc
            )
        )
    else:
        if start_date:
            query = query.filter(func.date(TokenUsage.created_at) >= start_date)
        if end_date:
            query = query.filter(func.date(TokenUsage.created_at) <= end_date)
    
    if combo:
        query = query.filter(TokenUsage.model == combo)
    if conversation_id:
        query = query.filter(TokenUsage.conversation_id == conversation_id)
    if request_type:
        query = query.filter(TokenUsage.request_type == request_type)
    
    # Get total count
    total = query.count()
    
    # Calculate pagination
    pages = math.ceil(total / page_size) if total > 0 else 1
    offset = (page - 1) * page_size
    
    # Get page results
    query = query.order_by(TokenUsage.created_at.desc())
    query = query.limit(page_size).offset(offset)
    results = query.all()
    
    # Build response
    items = []
    for token_usage, conversation_title in results:
        items.append(RequestDetail(
            id=token_usage.id,
            created_at=token_usage.created_at,
            conversation_id=token_usage.conversation_id,
            conversation_title=conversation_title,
            model=token_usage.model,
            input_tokens=token_usage.input_tokens,
            output_tokens=token_usage.output_tokens,
            total_tokens=token_usage.total_tokens,
            request_type=token_usage.request_type,
            rag_enabled=bool(token_usage.rag_enabled),
            knowledge_base_id=token_usage.knowledge_base_id,
            latency_ms=token_usage.latency_ms
        ))
    
    return RequestHistory(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages
    )
