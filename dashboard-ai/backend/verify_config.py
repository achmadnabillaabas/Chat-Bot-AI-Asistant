"""
Verify configuration is loaded correctly.
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.config import settings

print("=" * 60)
print("Configuration Verification")
print("=" * 60)
print()

print("9Router Configuration:")
print(f"  NINEROUTER_BASE_URL: {settings.NINEROUTER_BASE_URL}")
print(f"  NINEROUTER_API_KEY: {'[SET - ' + str(len(settings.NINEROUTER_API_KEY)) + ' chars]' if settings.NINEROUTER_API_KEY else '[NOT SET]'}")
print(f"  DEFAULT_MODEL: {settings.DEFAULT_MODEL}")
print()

print("Database Configuration:")
print(f"  DATABASE_URL: {settings.DATABASE_URL[:50]}...")
print()

print("Application Configuration:")
print(f"  FRONTEND_URL: {settings.FRONTEND_URL}")
print(f"  BACKEND_HOST: {settings.BACKEND_HOST}")
print(f"  BACKEND_PORT: {settings.BACKEND_PORT}")
print()

print("CORS Configuration:")
print(f"  CORS_ORIGINS: {settings.CORS_ORIGINS}")
print()

# Check critical settings
errors = []

if not settings.NINEROUTER_API_KEY:
    errors.append("❌ NINEROUTER_API_KEY is not set")
else:
    print(f"✅ NINEROUTER_API_KEY is set ({len(settings.NINEROUTER_API_KEY)} characters)")

if not settings.NINEROUTER_BASE_URL:
    errors.append("❌ NINEROUTER_BASE_URL is not set")
else:
    print(f"✅ NINEROUTER_BASE_URL is set: {settings.NINEROUTER_BASE_URL}")

if not settings.DEFAULT_MODEL:
    errors.append("❌ DEFAULT_MODEL is not set")
else:
    print(f"✅ DEFAULT_MODEL is set: {settings.DEFAULT_MODEL}")

print()

if errors:
    print("=" * 60)
    print("ERRORS FOUND:")
    print("=" * 60)
    for error in errors:
        print(error)
    print()
    print("Please check your .env file")
    sys.exit(1)
else:
    print("=" * 60)
    print("✅ Configuration is valid")
    print("=" * 60)
    sys.exit(0)
