"""
Telegram Bot API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
import logging
from datetime import datetime

from app.core.database import get_db
from app.schemas.telegram import (
    TelegramConnectRequest,
    TelegramStatusResponse,
    TelegramBotInfo,
    TelegramDisconnectResponse
)
from app.models.telegram_config import TelegramConfig
from app.services.telegram_service import telegram_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/telegram", tags=["telegram"])


@router.get("/status", response_model=TelegramStatusResponse)
async def get_telegram_status(db: Session = Depends(get_db)):
    """
    Get Telegram bot connection status.
    
    Returns bot info if connected, but never returns the raw token.
    """
    config = db.query(TelegramConfig).first()
    
    if not config or not config.is_connected:
        return TelegramStatusResponse(
            is_connected=False,
            bot_info=None,
            combo_id=None,
            connected_at=None
        )
    
    # Return safe bot information (never the token)
    return TelegramStatusResponse(
        is_connected=True,
        bot_info=TelegramBotInfo(
            bot_id=config.bot_id,
            bot_username=config.bot_username,
            bot_name=config.bot_name
        ) if config.bot_id else None,
        combo_id=config.combo_id,
        connected_at=config.last_connected_at
    )


@router.post("/connect", response_model=TelegramStatusResponse)
async def connect_telegram_bot(
    request: TelegramConnectRequest,
    db: Session = Depends(get_db)
):
    """
    Connect Telegram bot.
    
    1. Validates token with Telegram API (getMe)
    2. Saves configuration
    3. Starts polling
    4. Returns safe bot info (never the token)
    """
    logger.info("Attempting to connect Telegram bot")
    
    try:
        # Validate token with Telegram (will sanitize and check format)
        bot_info = await telegram_service.validate_token(request.bot_token)
        
        bot_id = bot_info.get("id")
        bot_username = bot_info.get("username")
        bot_name = bot_info.get("first_name")
        
        if not bot_id or not bot_username:
            logger.error("Invalid bot information from Telegram API")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid bot information received from Telegram"
            )
        
        # Sanitize token before saving
        sanitized_token = request.bot_token.strip().strip('"').strip("'")
        
        # Save or update configuration
        config = db.query(TelegramConfig).first()
        
        if config:
            # Update existing config
            config.bot_token = sanitized_token
            config.bot_id = bot_id
            config.bot_username = bot_username
            config.bot_name = bot_name
            config.combo_id = request.combo_id
            config.is_active = True
            config.is_connected = True
            config.last_connected_at = datetime.utcnow()
            config.updated_at = datetime.utcnow()
        else:
            # Create new config
            config = TelegramConfig(
                bot_token=sanitized_token,
                bot_id=bot_id,
                bot_username=bot_username,
                bot_name=bot_name,
                combo_id=request.combo_id,
                is_active=True,
                is_connected=True,
                last_connected_at=datetime.utcnow(),
                last_update_id=0
            )
            db.add(config)
        
        db.commit()
        db.refresh(config)
        
        logger.info(f"Telegram bot configured | username=@{bot_username} | combo={request.combo_id}")
        
        # Start polling
        telegram_service.start_polling(
            bot_token=sanitized_token,
            combo_id=request.combo_id,
            update_offset=config.last_update_id or 0
        )
        
        # Return safe response (no token)
        return TelegramStatusResponse(
            is_connected=True,
            bot_info=TelegramBotInfo(
                bot_id=bot_id,
                bot_username=bot_username,
                bot_name=bot_name
            ),
            combo_id=request.combo_id,
            connected_at=config.last_connected_at
        )
    
    except ValueError as e:
        # These are safe user-facing errors from validate_token
        logger.error(f"Telegram bot validation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to connect Telegram bot: {type(e).__name__}: {str(e)}", exc_info=True)
        
        # Return safe generic error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to connect bot. Please try again."
        )


@router.post("/disconnect", response_model=TelegramDisconnectResponse)
async def disconnect_telegram_bot(db: Session = Depends(get_db)):
    """
    Disconnect Telegram bot.
    
    1. Stops polling
    2. Updates configuration status
    3. Does NOT delete conversations or token usage
    """
    logger.info("Disconnecting Telegram bot")
    
    config = db.query(TelegramConfig).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Telegram bot not configured"
        )
    
    # Stop polling
    telegram_service.stop_polling()
    
    # Update configuration
    config.is_connected = False
    config.is_active = False
    config.updated_at = datetime.utcnow()
    db.commit()
    
    logger.info("Telegram bot disconnected")
    
    return TelegramDisconnectResponse(
        message="Telegram bot disconnected successfully",
        is_connected=False
    )
