"""
FastAPI main application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from app.core.config import settings
from app.api import router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Assistant API",
    description="Enterprise AI Assistant with RAG, Token Analytics, and Telegram integration",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(router, prefix="/api")


@app.on_event("startup")
async def startup_event():
    """Log startup information and start Telegram polling if configured."""
    logger.info("=" * 60)
    logger.info("AI Assistant API Starting")
    logger.info("=" * 60)
    logger.info(f"9Router URL: {settings.NINEROUTER_BASE_URL}")
    logger.info(f"Default Model: {settings.DEFAULT_MODEL}")
    logger.info(f"CORS Origins: {settings.CORS_ORIGINS}")
    logger.info("=" * 60)
    
    # Start Telegram polling if configured
    try:
        from app.core.database import SessionLocal
        from app.models.telegram_config import TelegramConfig
        from app.services.telegram_service import telegram_service
        
        db = SessionLocal()
        try:
            config = db.query(TelegramConfig).first()
            
            if config and config.is_active and config.is_connected and config.bot_token:
                logger.info("Starting Telegram bot polling from startup")
                telegram_service.start_polling(
                    bot_token=config.bot_token,
                    combo_id=config.combo_id or settings.DEFAULT_MODEL,
                    update_offset=config.last_update_id or 0
                )
                logger.info(f"Telegram bot started | username=@{config.bot_username}")
            else:
                logger.info("Telegram bot not configured or disabled")
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Failed to start Telegram bot on startup: {str(e)}")


@app.on_event("shutdown")
async def shutdown_event():
    """Stop Telegram polling on shutdown."""
    logger.info("Stopping Telegram bot polling")
    try:
        from app.services.telegram_service import telegram_service
        telegram_service.stop_polling()
    except Exception as e:
        logger.error(f"Error stopping Telegram bot: {str(e)}")


@app.get("/")
async def root():
    """Root endpoint - API health check."""
    return {
        "status": "online",
        "service": "AI Assistant API",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    from app.services.ninerouter_service import ninerouter_service
    
    ninerouter_healthy = await ninerouter_service.health_check()
    
    return {
        "status": "healthy" if ninerouter_healthy else "degraded",
        "database": "connected",
        "9router": "connected" if ninerouter_healthy else "unavailable"
    }
