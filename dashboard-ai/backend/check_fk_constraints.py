"""
Check actual FK constraints directly from PostgreSQL.
"""
from sqlalchemy import create_engine, text
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)

print("=" * 70)
print("CHECK FOREIGN KEY CONSTRAINTS")
print("=" * 70)

with engine.connect() as conn:
    # Check alembic version
    result = conn.execute(text("SELECT version_num FROM alembic_version"))
    version = result.fetchone()[0]
    print(f"\nAlembic version: {version}")
    
    # Query PostgreSQL information_schema for FK constraints
    print("\n[1] TOKEN_USAGE FK CONSTRAINTS")
    print("-" * 70)
    result = conn.execute(text("""
        SELECT 
            tc.constraint_name,
            kcu.column_name,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name,
            rc.delete_rule
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
            ON tc.constraint_name = kcu.constraint_name
        JOIN information_schema.constraint_column_usage AS ccu
            ON ccu.constraint_name = tc.constraint_name
        JOIN information_schema.referential_constraints AS rc
            ON rc.constraint_name = tc.constraint_name
        WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_name = 'token_usage'
    """))
    for row in result:
        print(f"  {row[0]}")
        print(f"    Column: {row[1]} -> {row[2]}.{row[3]}")
        print(f"    ON DELETE: {row[4]}")
        print()
    
    print("\n[2] DOCUMENTS FK CONSTRAINTS")
    print("-" * 70)
    result = conn.execute(text("""
        SELECT 
            tc.constraint_name,
            kcu.column_name,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name,
            rc.delete_rule
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
            ON tc.constraint_name = kcu.constraint_name
        JOIN information_schema.constraint_column_usage AS ccu
            ON ccu.constraint_name = tc.constraint_name
        JOIN information_schema.referential_constraints AS rc
            ON rc.constraint_name = tc.constraint_name
        WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_name = 'documents'
    """))
    for row in result:
        print(f"  {row[0]}")
        print(f"    Column: {row[1]} -> {row[2]}.{row[3]}")
        print(f"    ON DELETE: {row[4]}")
        print()
    
    print("\n[3] DOCUMENT_CHUNKS FK CONSTRAINTS")
    print("-" * 70)
    result = conn.execute(text("""
        SELECT 
            tc.constraint_name,
            kcu.column_name,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name,
            rc.delete_rule
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
            ON tc.constraint_name = kcu.constraint_name
        JOIN information_schema.constraint_column_usage AS ccu
            ON ccu.constraint_name = tc.constraint_name
        JOIN information_schema.referential_constraints AS rc
            ON rc.constraint_name = tc.constraint_name
        WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_name = 'document_chunks'
    """))
    for row in result:
        print(f"  {row[0]}")
        print(f"    Column: {row[1]} -> {row[2]}.{row[3]}")
        print(f"    ON DELETE: {row[4]}")
        print()

print("=" * 70)
