"""
API routes package.
"""
from fastapi import APIRouter

router = APIRouter()

# Import routes
from app.api import chat, conversations, models, analytics, telegram, knowledge_bases, documents, rag

# Include routers
router.include_router(chat.router)
router.include_router(conversations.router)
router.include_router(models.router)  # Now serves combos at /api/combos
router.include_router(analytics.router)  # Token usage analytics
router.include_router(telegram.router)  # Telegram bot management
router.include_router(knowledge_bases.router)  # Knowledge Base management
router.include_router(documents.router)  # Document upload and management
router.include_router(rag.router)  # RAG search

__all__ = ["router"]
