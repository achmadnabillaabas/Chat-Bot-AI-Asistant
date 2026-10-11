"""
Telegram Bot service for message polling and processing.
"""
import httpx
import asyncio
import logging
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database import get_db, SessionLocal
from app.models.telegram_config import TelegramConfig
from app.models.user import User
from app.models.conversation import Conversation, Message
from app.models.token_usage import TokenUsage
from app.services.ninerouter_service import ninerouter_service

logger = logging.getLogger(__name__)


class TelegramService:
    """Service for Telegram bot polling and message handling."""
    
    def __init__(self):
        self.is_running = False
        self.polling_task: Optional[asyncio.Task] = None
        self.bot_token: Optional[str] = None
        self.combo_id: Optional[str] = None
        self.update_offset: int = 0
        self.timeout = 30  # Long polling timeout
        
    def get_api_url(self, method: str) -> str:
        """Get Telegram Bot API URL for a method."""
        if not self.bot_token:
            raise ValueError("Bot token not configured")
        return f"https://api.telegram.org/bot{self.bot_token}/{method}"
    
    async def validate_token(self, bot_token: str) -> Dict[str, Any]:
        """
        Validate Telegram bot token using getMe.
        
        Returns:
            Bot information dict with id, username, first_name
            
        Raises:
            ValueError: If token format is invalid or API returns error
            httpx.HTTPError: If HTTP request fails
        """
        # Sanitize token: strip whitespace, remove quotes
        sanitized_token = bot_token.strip().strip('"').strip("'")
        
        if not sanitized_token:
            raise ValueError("Bot token cannot be empty")
        
        # Basic token format validation (without exposing the token)
        # Telegram bot tokens are typically in format: NUMBER:ALPHANUMERIC
        if ':' not in sanitized_token:
            logger.error("Invalid token format: missing ':' separator")
            raise ValueError("Invalid token format")
        
        logger.info("Validating Telegram bot token with getMe API")
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Construct URL (do not log the complete URL with token)
                url = f"https://api.telegram.org/bot{sanitized_token}/getMe"
                
                response = await client.get(url)
                
                # Log safe diagnostic info
                logger.info(f"Telegram API response | method=getMe | status={response.status_code}")
                
                # Handle specific HTTP errors
                if response.status_code == 404:
                    logger.error("Telegram API returned 404 - invalid bot token")
                    raise ValueError("Invalid bot token")
                elif response.status_code == 401:
                    logger.error("Telegram API returned 401 - unauthorized")
                    raise ValueError("Unauthorized bot token")
                
                response.raise_for_status()
                data = response.json()
                
                if not data.get("ok"):
                    error_desc = data.get('description', 'Unknown error')
                    logger.error(f"Telegram API error | description={error_desc}")
                    raise ValueError(f"Telegram API error: {error_desc}")
                
                bot_info = data["result"]
                logger.info(f"Bot validated | username=@{bot_info.get('username')} | id={bot_info.get('id')}")
                
                return bot_info
                
        except httpx.TimeoutException:
            logger.error("Telegram API request timeout")
            raise ValueError("Connection to Telegram API timed out")
        except httpx.HTTPStatusError as e:
            logger.error(f"Telegram API HTTP error | status={e.response.status_code}")
            if e.response.status_code == 404:
                raise ValueError("Invalid bot token")
            elif e.response.status_code == 401:
                raise ValueError("Unauthorized bot token")
            else:
                raise ValueError(f"Telegram API error (HTTP {e.response.status_code})")
        except httpx.RequestError as e:
            logger.error(f"Telegram API request error | type={type(e).__name__}")
            raise ValueError("Failed to connect to Telegram API")
        except ValueError:
            # Re-raise ValueError as-is
            raise
        except Exception as e:
            logger.error(f"Unexpected error validating token | type={type(e).__name__} | error={str(e)}")
            raise ValueError("Failed to validate bot token")
    
    async def send_message(self, chat_id: int, text: str) -> bool:
        """
        Send a message to a Telegram chat.
        
        Args:
            chat_id: Telegram chat ID
            text: Message text
            
        Returns:
            True if successful
        """
        if not self.bot_token:
            logger.error("Cannot send message: bot token not configured")
            return False
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    self.get_api_url("sendMessage"),
                    json={
                        "chat_id": chat_id,
                        "text": text,
                        "parse_mode": "Markdown"
                    }
                )
                response.raise_for_status()
                return True
        except Exception as e:
            logger.error(f"Failed to send Telegram message | chat_id={chat_id} | error={str(e)}")
            return False
    
    def get_or_create_telegram_user(self, telegram_user: Dict[str, Any], db: Session) -> User:
        """
        Get or create application user from Telegram user.
        
        Args:
            telegram_user: Telegram user dict with id, username, first_name, last_name
            db: Database session
            
        Returns:
            User model instance
        """
        telegram_id = telegram_user.get("id")
        username = telegram_user.get("username") or f"telegram_{telegram_id}"
        first_name = telegram_user.get("first_name", "")
        last_name = telegram_user.get("last_name", "")
        full_name = f"{first_name} {last_name}".strip() or username
        
        # Create unique email for Telegram users
        email = f"telegram_{telegram_id}@telegram.local"
        
        # Check if user exists
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            user = User(
                email=email,
                username=username,
                hashed_password="telegram",  # Not used for Telegram auth
                full_name=full_name,
                role="user",
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info(f"Created Telegram user | telegram_id={telegram_id} | user_id={user.id}")
        
        return user
    
    def get_or_create_conversation(self, user_id: int, telegram_chat_id: int, db: Session) -> Conversation:
        """
        Get or create conversation for Telegram user.
        
        Args:
            user_id: Application user ID
            telegram_chat_id: Telegram chat ID
            db: Database session
            
        Returns:
            Conversation instance
        """
        # Find active Telegram conversation for this user
        # We use conversation title to store telegram_chat_id for now
        # In production, you might add a channel/source field
        
        conversation = db.query(Conversation).filter(
            Conversation.user_id == user_id
        ).order_by(Conversation.updated_at.desc()).first()
        
        # If no conversation or user sent /new command, create new one
        if not conversation:
            conversation = Conversation(
                user_id=user_id,
                title=f"Telegram Chat {telegram_chat_id}"
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
            logger.info(f"Created Telegram conversation | conversation_id={conversation.id} | user_id={user_id}")
        
        return conversation
    
    def reset_conversation(self, user_id: int, telegram_chat_id: int, db: Session) -> Conversation:
        """
        Create a new conversation (equivalent to /new command).
        
        Args:
            user_id: Application user ID
            telegram_chat_id: Telegram chat ID
            db: Database session
            
        Returns:
            New conversation instance
        """
        conversation = Conversation(
            user_id=user_id,
            title=f"Telegram Chat {telegram_chat_id}"
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        logger.info(f"Reset Telegram conversation | new_conversation_id={conversation.id} | user_id={user_id}")
        return conversation
    
    async def process_message(self, telegram_message: Dict[str, Any], db: Session):
        """
        Process incoming Telegram message and send AI response.
        
        Args:
            telegram_message: Telegram message dict
            db: Database session
        """
        chat_id = telegram_message.get("chat", {}).get("id")
        message_text = telegram_message.get("text", "").strip()
        telegram_user = telegram_message.get("from")
        
        if not chat_id or not message_text or not telegram_user:
            logger.warning("Invalid Telegram message format")
            return
        
        logger.info(f"[Telegram] Processing message | chat_id={chat_id} | text_length={len(message_text)}")
        
        try:
            # Stage 1: Get or create user
            logger.info(f"[Telegram] Stage 1: User mapping | telegram_id={telegram_user.get('id')}")
            user = self.get_or_create_telegram_user(telegram_user, db)
            logger.info(f"[Telegram] User mapped | user_id={user.id} | email={user.email}")
            
            # Handle commands
            if message_text == "/start":
                logger.info(f"[Telegram] Command: /start")
                await self.send_message(
                    chat_id,
                    "Hello! I am your AI Assistant.\nSend me a message to start chatting."
                )
                return
            
            elif message_text == "/help":
                logger.info(f"[Telegram] Command: /help")
                await self.send_message(
                    chat_id,
                    "🤖 *AI Assistant Help*\n\n"
                    "• Send any message to chat with AI\n"
                    "• /new - Start a new conversation\n"
                    "• /help - Show this help message\n\n"
                    f"Current AI: {self.combo_id or 'Default'}"
                )
                return
            
            elif message_text == "/new":
                logger.info(f"[Telegram] Command: /new")
                self.reset_conversation(user.id, chat_id, db)
                await self.send_message(
                    chat_id,
                    "✨ Started a new conversation!\nWhat would you like to talk about?"
                )
                return
            
            # Normal message - process with AI
            logger.info(f"[Telegram] Stage 2: Conversation lookup")
            conversation = self.get_or_create_conversation(user.id, chat_id, db)
            logger.info(f"[Telegram] Conversation ready | conversation_id={conversation.id}")
            
            # Stage 3: Save user message
            logger.info(f"[Telegram] Stage 3: Saving user message")
            user_message = Message(
                conversation_id=conversation.id,
                role="user",
                content=message_text
            )
            db.add(user_message)
            db.commit()
            db.refresh(user_message)
            logger.info(f"[Telegram] User message saved | message_id={user_message.id}")
            
            # Stage 4: Load conversation history
            logger.info(f"[Telegram] Stage 4: Loading conversation history")
            previous_messages = db.query(Message).filter(
                Message.conversation_id == conversation.id,
                Message.id < user_message.id
            ).order_by(Message.created_at.desc()).limit(10).all()
            
            previous_messages.reverse()
            
            # Build messages for AI
            messages_for_ai = []
            for msg in previous_messages:
                messages_for_ai.append({
                    "role": msg.role,
                    "content": msg.content
                })
            
            messages_for_ai.append({
                "role": "user",
                "content": message_text
            })
            logger.info(f"[Telegram] Context built | total_messages={len(messages_for_ai)}")
            
            # Stage 5: Call 9Router
            logger.info(f"[Telegram] Stage 5: Calling 9Router | combo={self.combo_id}")
            try:
                ai_response = await ninerouter_service.chat_completion(
                    messages=messages_for_ai,
                    model=self.combo_id
                )
                logger.info(f"[Telegram] 9Router success | model={ai_response.get('model')} | tokens={ai_response.get('usage', {}).get('total_tokens')}")
            except Exception as e:
                logger.error(f"[Telegram] 9Router failed | type={type(e).__name__} | error={str(e)}", exc_info=True)
                await self.send_message(
                    chat_id,
                    "Maaf, terjadi kesalahan saat memproses pesan."
                )
                return
            
            # Stage 6: Save assistant message
            logger.info(f"[Telegram] Stage 6: Saving assistant message")
            assistant_message = Message(
                conversation_id=conversation.id,
                role="assistant",
                content=ai_response["content"],
                model=ai_response["model"]
            )
            db.add(assistant_message)
            db.commit()
            db.refresh(assistant_message)
            logger.info(f"[Telegram] Assistant message saved | message_id={assistant_message.id}")
            
            # Stage 7: Save token usage
            logger.info(f"[Telegram] Stage 7: Saving token usage")
            token_usage = TokenUsage(
                user_id=user.id,
                conversation_id=conversation.id,
                message_id=assistant_message.id,
                model=ai_response["model"],
                input_tokens=ai_response["usage"]["input_tokens"],
                output_tokens=ai_response["usage"]["output_tokens"],
                total_tokens=ai_response["usage"]["total_tokens"],
                request_type="telegram",
                rag_enabled=0  # Integer 0 for non-RAG requests
            )
            db.add(token_usage)
            db.commit()
            
            logger.info(
                f"[Telegram] Token usage saved | "
                f"input={token_usage.input_tokens} | "
                f"output={token_usage.output_tokens} | "
                f"total={token_usage.total_tokens}"
            )
            
            # Stage 8: Send response to Telegram
            logger.info(f"[Telegram] Stage 8: Sending response to chat")
            success = await self.send_message(chat_id, ai_response["content"])
            if success:
                logger.info(f"[Telegram] Response sent successfully | chat_id={chat_id}")
            else:
                logger.error(f"[Telegram] Failed to send response to Telegram | chat_id={chat_id}")
            
        except Exception as e:
            logger.error(f"[Telegram] Error processing message | type={type(e).__name__} | error={str(e)}", exc_info=True)
            try:
                await self.send_message(
                    chat_id,
                    "Maaf, terjadi kesalahan saat memproses pesan."
                )
            except:
                pass
    
    async def poll_updates(self):
        """
        Long poll for Telegram updates.
        """
        logger.info("[Telegram] Polling loop started")
        
        while self.is_running:
            try:
                async with httpx.AsyncClient(timeout=self.timeout + 10) as client:
                    response = await client.get(
                        self.get_api_url("getUpdates"),
                        params={
                            "offset": self.update_offset,
                            "timeout": self.timeout
                        }
                    )
                    
                    # Handle 409 Conflict (another instance polling)
                    if response.status_code == 409:
                        logger.error(
                            "[Telegram] HTTP 409 Conflict - another instance is polling. "
                            "Stopping this poller to prevent conflicts."
                        )
                        self.is_running = False
                        break
                    
                    response.raise_for_status()
                    data = response.json()
                    
                    if not data.get("ok"):
                        error_desc = data.get('description', 'Unknown error')
                        logger.error(f"[Telegram] API error: {error_desc}")
                        await asyncio.sleep(5)
                        continue
                    
                    updates = data.get("result", [])
                    
                    if updates:
                        logger.info(f"[Telegram] Received {len(updates)} updates")
                        
                        # Process each update
                        for update in updates:
                            update_id = update.get("update_id")
                            
                            if update_id:
                                # Update offset to prevent duplicate processing
                                self.update_offset = update_id + 1
                                
                                # Process message
                                message = update.get("message")
                                if message:
                                    # Create new DB session for each message
                                    db = SessionLocal()
                                    try:
                                        await self.process_message(message, db)
                                    finally:
                                        db.close()
                        
                        # Save offset to database
                        db = SessionLocal()
                        try:
                            config = db.query(TelegramConfig).first()
                            if config:
                                config.last_update_id = self.update_offset
                                db.commit()
                        finally:
                            db.close()
            
            except asyncio.CancelledError:
                logger.info("[Telegram] Polling cancelled")
                break
            except httpx.TimeoutException:
                # Timeout is expected with long polling, continue
                continue
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 409:
                    logger.error("[Telegram] HTTP 409 - stopping poller")
                    self.is_running = False
                    break
                logger.error(f"[Telegram] HTTP error | status={e.response.status_code}")
                await asyncio.sleep(5)
            except httpx.HTTPError as e:
                logger.error(f"[Telegram] API HTTP error: {str(e)}")
                await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"[Telegram] Polling error | type={type(e).__name__} | error={str(e)}", exc_info=True)
                await asyncio.sleep(5)
        
        logger.info("[Telegram] Polling loop stopped")
    
    def start_polling(self, bot_token: str, combo_id: str, update_offset: int = 0):
        """
        Start polling for Telegram updates.
        
        Args:
            bot_token: Telegram bot token
            combo_id: AI Combo ID to use
            update_offset: Last processed update ID
        """
        if self.is_running:
            logger.warning("[Telegram] Polling already running - skipping start")
            return
        
        # Stop any existing task first (safety measure)
        if self.polling_task and not self.polling_task.done():
            logger.warning("[Telegram] Found existing polling task - cancelling it first")
            self.polling_task.cancel()
            self.polling_task = None
        
        self.bot_token = bot_token
        self.combo_id = combo_id
        self.update_offset = update_offset
        self.is_running = True
        
        # Start polling in background
        self.polling_task = asyncio.create_task(self.poll_updates())
        logger.info(f"[Telegram] Polling started | combo={combo_id} | offset={update_offset}")
    
    def stop_polling(self):
        """Stop polling for Telegram updates."""
        if not self.is_running:
            logger.warning("[Telegram] Polling not running - nothing to stop")
            return
        
        logger.info("[Telegram] Stopping polling...")
        self.is_running = False
        
        if self.polling_task and not self.polling_task.done():
            self.polling_task.cancel()
            logger.info("[Telegram] Polling task cancelled")
        
        self.polling_task = None
        self.bot_token = None
        self.combo_id = None
        
        logger.info("[Telegram] Polling stopped successfully")


# Singleton instance
telegram_service = TelegramService()
