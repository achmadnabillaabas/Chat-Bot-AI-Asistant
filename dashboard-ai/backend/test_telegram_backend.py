"""
Test script for Telegram bot backend functionality.
"""
import sys
import asyncio

async def test_telegram_imports():
    """Test that all Telegram modules can be imported."""
    print("Testing Telegram Backend Implementation")
    print("=" * 60)
    
    try:
        print("\n1. Testing imports...")
        from app.schemas.telegram import (
            TelegramConnectRequest,
            TelegramStatusResponse,
            TelegramBotInfo
        )
        print("   ✓ Telegram schemas imported")
        
        from app.services.telegram_service import telegram_service
        print("   ✓ Telegram service imported")
        
        from app.api.telegram import router
        print("   ✓ Telegram API router imported")
        
        from app.models.telegram_config import TelegramConfig
        print("   ✓ Telegram config model imported")
        
        print("\n2. Testing telegram service methods...")
        print(f"   ✓ telegram_service.is_running = {telegram_service.is_running}")
        print(f"   ✓ telegram_service.bot_token = {telegram_service.bot_token}")
        
        print("\n3. Testing API router...")
        routes = [route.path for route in router.routes]
        print(f"   ✓ Telegram routes: {routes}")
        
        print("\n" + "=" * 60)
        print("✓ All Telegram backend components loaded successfully!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_telegram_imports())
    sys.exit(0 if result else 1)
