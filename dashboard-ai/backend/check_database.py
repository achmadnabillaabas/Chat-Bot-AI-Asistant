"""
Database diagnostic script.
Check if tables exist and show their structure.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import engine
from app.core.config import settings
from sqlalchemy import inspect, text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_database():
    """Check database connection and tables."""
    print("=" * 60)
    print("Database Diagnostic")
    print("=" * 60)
    print()
    
    print(f"Database URL: {settings.DATABASE_URL[:50]}...")
    print()
    
    try:
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection successful")
            print()
            
            # Get inspector
            inspector = inspect(engine)
            
            # List all tables
            tables = inspector.get_table_names()
            print(f"Tables in database: {len(tables)}")
            for table in sorted(tables):
                print(f"  - {table}")
            print()
            
            # Check required tables
            required_tables = ['users', 'conversations', 'messages', 'token_usage']
            missing_tables = [t for t in required_tables if t not in tables]
            
            if missing_tables:
                print("❌ Missing required tables:")
                for table in missing_tables:
                    print(f"  - {table}")
                print()
                print("Run: python create_db.py")
                return False
            else:
                print("✅ All required tables exist")
                print()
            
            # Check users table structure
            if 'users' in tables:
                print("Users table columns:")
                for column in inspector.get_columns('users'):
                    nullable = "NULL" if column['nullable'] else "NOT NULL"
                    print(f"  - {column['name']}: {column['type']} {nullable}")
                print()
                
                # Check if demo user exists
                result = conn.execute(text("SELECT COUNT(*) FROM users WHERE email = 'demo@aiassistant.local'"))
                count = result.scalar()
                if count > 0:
                    print(f"✅ Demo user exists (count: {count})")
                else:
                    print("⚠️  Demo user does not exist (will be created on first request)")
                print()
            
            # Check conversations table structure
            if 'conversations' in tables:
                print("Conversations table columns:")
                for column in inspector.get_columns('conversations'):
                    nullable = "NULL" if column['nullable'] else "NOT NULL"
                    print(f"  - {column['name']}: {column['type']} {nullable}")
                print()
                
                # Check conversation count
                result = conn.execute(text("SELECT COUNT(*) FROM conversations"))
                count = result.scalar()
                print(f"Conversations in database: {count}")
                print()
            
            # Check messages table
            if 'messages' in tables:
                print("Messages table columns:")
                for column in inspector.get_columns('messages'):
                    nullable = "NULL" if column['nullable'] else "NOT NULL"
                    print(f"  - {column['name']}: {column['type']} {nullable}")
                print()
                
                # Check message count
                result = conn.execute(text("SELECT COUNT(*) FROM messages"))
                count = result.scalar()
                print(f"Messages in database: {count}")
                print()
            
            print("=" * 60)
            print("✅ Database check complete")
            print("=" * 60)
            return True
            
    except Exception as e:
        print(f"❌ Database error: {type(e).__name__}")
        print(f"   {str(e)}")
        print()
        print("Possible causes:")
        print("  - PostgreSQL not running")
        print("  - Wrong connection URL")
        print("  - Database does not exist")
        print("  - Tables not created")
        print()
        print("Try:")
        print("  1. Check PostgreSQL is running")
        print("  2. Verify DATABASE_URL in .env")
        print("  3. Run: python create_db.py")
        return False

if __name__ == "__main__":
    success = check_database()
    sys.exit(0 if success else 1)
