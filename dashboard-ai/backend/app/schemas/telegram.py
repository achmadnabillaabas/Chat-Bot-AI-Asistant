"""
Telegram Bot schemas for API requests and responses.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TelegramConnectRequest(BaseModel):
    """Request to connect Telegram bot."""
    bot_token: str = Field(..., min_length=10, description="Telegram Bot API token")
    combo_id: str = Field(..., description="AI Combo ID to use for bot responses")


class TelegramBotInfo(BaseModel):
    """Telegram bot information."""
    bot_id: int
    bot_username: str
    bot_name: str
    
    class Config:
        from_attributes = True


class TelegramStatusResponse(BaseModel):
    """Telegram bot status response."""
    is_connected: bool
    bot_info: Optional[TelegramBotInfo] = None
    combo_id: Optional[str] = None
    connected_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class TelegramDisconnectResponse(BaseModel):
    """Response after disconnecting bot."""
    message: str
    is_connected: bool
