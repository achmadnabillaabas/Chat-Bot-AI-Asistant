"""Check actual database schema."""
from sqlalchemy import inspect
from app.core.database import engine

insp = inspect(engine)

print("=== KNOWLEDGE_BASES TABLE ===")
if insp.has_table('knowledge_bases'):
    cols = insp.get_columns('knowledge_bases')
    print("Columns:")
    for c in cols:
        nullable = "NULL" if c['nullable'] else "NOT NULL"
        print(f"  - {c['name']}: {c['type']} {nullable}")
    
    print("\nForeign Keys:")
    fks = insp.get_foreign_keys('knowledge_bases')
    for fk in fks:
        print(f"  - {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
    
    print("\nIndexes:")
    indexes = insp.get_indexes('knowledge_bases')
    for idx in indexes:
        print(f"  - {idx['name']}: {idx['column_names']}")
else:
    print("Table does not exist!")

print("\n=== DOCUMENTS TABLE ===")
if insp.has_table('documents'):
    cols = insp.get_columns('documents')
    print("Columns:")
    for c in cols:
        nullable = "NULL" if c['nullable'] else "NOT NULL"
        print(f"  - {c['name']}: {c['type']} {nullable}")
else:
    print("Table does not exist!")

print("\n=== DOCUMENT_CHUNKS TABLE ===")
if insp.has_table('document_chunks'):
    cols = insp.get_columns('document_chunks')
    print("Columns:")
    for c in cols:
        nullable = "NULL" if c['nullable'] else "NOT NULL"
        print(f"  - {c['name']}: {c['type']} {nullable}")
else:
    print("Table does not exist!")

print("\n=== ALEMBIC VERSION ===")
if insp.has_table('alembic_version'):
    from app.core.database import SessionLocal
    db = SessionLocal()
    result = db.execute("SELECT version_num FROM alembic_version").fetchone()
    if result:
        print(f"Current revision: {result[0]}")
    else:
        print("No version recorded")
    db.close()
