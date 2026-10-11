"""
Inspect actual PostgreSQL schema and foreign key constraints.
"""
from sqlalchemy import create_engine, inspect, text
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
inspector = inspect(engine)

print("=" * 70)
print("POSTGRESQL SCHEMA INSPECTION")
print("=" * 70)

# Check token_usage table
print("\n[1] TOKEN_USAGE TABLE")
print("-" * 70)
columns = inspector.get_columns('token_usage')
for col in columns:
    nullable = "NULL" if col['nullable'] else "NOT NULL"
    print(f"  {col['name']:30s} {str(col['type']):20s} {nullable}")

print("\n[2] TOKEN_USAGE FOREIGN KEYS")
print("-" * 70)
fks = inspector.get_foreign_keys('token_usage')
for fk in fks:
    print(f"  Constraint: {fk['name']}")
    print(f"    Columns: {fk['constrained_columns']}")
    print(f"    References: {fk['referred_table']}.{fk['referred_columns']}")
    print(f"    On Delete: {fk.get('ondelete', 'NO ACTION')}")
    print()

# Check knowledge_bases table
print("\n[3] KNOWLEDGE_BASES TABLE")
print("-" * 70)
columns = inspector.get_columns('knowledge_bases')
for col in columns:
    nullable = "NULL" if col['nullable'] else "NOT NULL"
    print(f"  {col['name']:30s} {str(col['type']):20s} {nullable}")

# Check documents table
print("\n[4] DOCUMENTS TABLE")
print("-" * 70)
columns = inspector.get_columns('documents')
for col in columns:
    nullable = "NULL" if col['nullable'] else "NOT NULL"
    print(f"  {col['name']:30s} {str(col['type']):20s} {nullable}")

print("\n[5] DOCUMENTS FOREIGN KEYS")
print("-" * 70)
fks = inspector.get_foreign_keys('documents')
for fk in fks:
    print(f"  Constraint: {fk['name']}")
    print(f"    Columns: {fk['constrained_columns']}")
    print(f"    References: {fk['referred_table']}.{fk['referred_columns']}")
    print(f"    On Delete: {fk.get('ondelete', 'NO ACTION')}")
    print()

# Check document_chunks table
print("\n[6] DOCUMENT_CHUNKS FOREIGN KEYS")
print("-" * 70)
fks = inspector.get_foreign_keys('document_chunks')
for fk in fks:
    print(f"  Constraint: {fk['name']}")
    print(f"    Columns: {fk['constrained_columns']}")
    print(f"    References: {fk['referred_table']}.{fk['referred_columns']}")
    print(f"    On Delete: {fk.get('ondelete', 'NO ACTION')}")
    print()

# Query token_usage data
print("\n[7] SAMPLE TOKEN_USAGE DATA")
print("-" * 70)
with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT id, knowledge_base_id, rag_enabled, request_type, created_at
        FROM token_usage
        ORDER BY created_at DESC
        LIMIT 10
    """))
    rows = result.fetchall()
    if rows:
        print(f"  {'ID':<6} {'KB_ID':<8} {'RAG':<6} {'TYPE':<12} {'CREATED'}")
        print("  " + "-" * 60)
        for row in rows:
            kb_id = str(row[1]) if row[1] is not None else "NULL"
            rag = "ON" if row[2] else "OFF"
            print(f"  {row[0]:<6} {kb_id:<8} {rag:<6} {row[3]:<12} {str(row[4])[:19]}")
    else:
        print("  No token_usage records found")

# Check if there are any token_usage records with KB references
print("\n[8] TOKEN_USAGE WITH KB REFERENCES")
print("-" * 70)
with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT tu.id, tu.knowledge_base_id, kb.name as kb_name, tu.rag_enabled
        FROM token_usage tu
        LEFT JOIN knowledge_bases kb ON tu.knowledge_base_id = kb.id
        WHERE tu.knowledge_base_id IS NOT NULL
        ORDER BY tu.created_at DESC
        LIMIT 5
    """))
    rows = result.fetchall()
    if rows:
        for row in rows:
            kb_exists = "EXISTS" if row[2] is not None else "DELETED"
            print(f"  Token #{row[0]} -> KB #{row[1]} ({kb_exists})")
    else:
        print("  No token_usage with KB references found")

print("\n" + "=" * 70)
print("INSPECTION COMPLETE")
print("=" * 70)
