"""
Direct database verification of token_usage.knowledge_base_id
"""
from sqlalchemy import create_engine, text
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)

print("=" * 70)
print("DIRECT DATABASE VERIFICATION: TOKEN_USAGE.KNOWLEDGE_BASE_ID")
print("=" * 70)

with engine.connect() as conn:
    # Get last 10 token_usage records
    print("\n[1] LAST 10 TOKEN_USAGE RECORDS")
    print("-" * 70)
    result = conn.execute(text("""
        SELECT 
            id,
            rag_enabled,
            knowledge_base_id,
            model,
            request_type,
            created_at
        FROM token_usage
        ORDER BY id DESC
        LIMIT 10
    """))
    
    rows = result.fetchall()
    if rows:
        print(f"  {'ID':<6} {'RAG':<6} {'KB_ID':<8} {'MODEL':<20} {'TYPE':<12} {'CREATED'}")
        print("  " + "-" * 70)
        for row in rows:
            rag = "ON " if row[1] else "OFF"
            kb_id = str(row[2]) if row[2] is not None else "NULL"
            print(f"  {row[0]:<6} {rag:<6} {kb_id:<8} {row[3]:<20} {row[4]:<12} {str(row[5])[:19]}")
    else:
        print("  No records found")
    
    # Check RAG ON with KB ID
    print("\n[2] RAG ON REQUESTS (should have KB ID)")
    print("-" * 70)
    result = conn.execute(text("""
        SELECT 
            id,
            knowledge_base_id,
            model,
            created_at
        FROM token_usage
        WHERE rag_enabled = 1
        ORDER BY id DESC
        LIMIT 5
    """))
    
    rows = result.fetchall()
    if rows:
        rag_on_count = 0
        rag_on_with_kb = 0
        for row in rows:
            rag_on_count += 1
            kb_status = "✅ HAS KB" if row[1] else "❌ NULL"
            if row[1]:
                rag_on_with_kb += 1
            print(f"  Token #{row[0]:4d} -> KB #{row[1] if row[1] else 'NULL':4s} {kb_status}")
        
        print(f"\n  RAG ON requests: {rag_on_count}")
        print(f"  With KB ID: {rag_on_with_kb}")
        print(f"  Without KB ID: {rag_on_count - rag_on_with_kb}")
        
        if rag_on_with_kb == rag_on_count:
            print(f"\n  ✅ ALL RAG ON REQUESTS HAVE KB ID")
        else:
            print(f"\n  ❌ SOME RAG ON REQUESTS MISSING KB ID")
    else:
        print("  No RAG ON requests found")
    
    # Check RAG OFF
    print("\n[3] RAG OFF REQUESTS (should have NULL KB ID)")
    print("-" * 70)
    result = conn.execute(text("""
        SELECT 
            id,
            knowledge_base_id,
            model,
            created_at
        FROM token_usage
        WHERE rag_enabled = 0
        ORDER BY id DESC
        LIMIT 5
    """))
    
    rows = result.fetchall()
    if rows:
        rag_off_count = 0
        rag_off_null = 0
        for row in rows:
            rag_off_count += 1
            kb_status = "✅ NULL" if row[1] is None else "❌ HAS KB"
            if row[1] is None:
                rag_off_null += 1
            print(f"  Token #{row[0]:4d} -> KB #{row[1] if row[1] else 'NULL':4s} {kb_status}")
        
        print(f"\n  RAG OFF requests: {rag_off_count}")
        print(f"  With NULL KB: {rag_off_null}")
        
        if rag_off_null == rag_off_count:
            print(f"\n  ✅ ALL RAG OFF REQUESTS HAVE NULL KB ID")
        else:
            print(f"\n  ⚠️  SOME RAG OFF REQUESTS HAVE KB ID (unusual)")
    else:
        print("  No RAG OFF requests found")
    
    # Check FK constraint behavior
    print("\n[4] FK CONSTRAINT TEST (token_usage with deleted KB)")
    print("-" * 70)
    result = conn.execute(text("""
        SELECT 
            tu.id,
            tu.knowledge_base_id,
            kb.name as kb_name,
            CASE 
                WHEN kb.id IS NULL AND tu.knowledge_base_id IS NOT NULL THEN 'ORPHANED'
                WHEN kb.id IS NOT NULL THEN 'EXISTS'
                ELSE 'NULL'
            END as kb_status
        FROM token_usage tu
        LEFT JOIN knowledge_bases kb ON tu.knowledge_base_id = kb.id
        WHERE tu.rag_enabled = 1
        ORDER BY tu.id DESC
        LIMIT 5
    """))
    
    rows = result.fetchall()
    if rows:
        for row in rows:
            status_display = "❌ ORPHANED (FK not working)" if row[3] == 'ORPHANED' else "✅ " + row[3]
            print(f"  Token #{row[0]:4d} -> KB #{row[1] if row[1] else 'NULL':4s} ({status_display})")
    else:
        print("  No RAG requests found")

print("\n" + "=" * 70)
print("VERIFICATION COMPLETE")
print("=" * 70)
