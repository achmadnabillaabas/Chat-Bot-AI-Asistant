"""
Quick script to check Telegram token usage in database.
"""
import psycopg2
from datetime import datetime

# Database connection
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="ai_assistant",
    user="user",
    password="password"
)

cur = conn.cursor()

# Check all token usage records
print("\n=== ALL TOKEN USAGE RECORDS ===")
cur.execute("""
    SELECT id, user_id, request_type, model, 
           input_tokens, output_tokens, total_tokens, 
           created_at, conversation_id
    FROM token_usage 
    ORDER BY created_at DESC 
    LIMIT 20
""")
rows = cur.fetchall()
print(f"Total records in last 20: {len(rows)}")
for row in rows:
    print(f"ID: {row[0]} | User: {row[1]} | Type: {row[2]} | Model: {row[3]} | "
          f"I/O/T: {row[4]}/{row[5]}/{row[6]} | Time: {row[7]} | Conv: {row[8]}")

# Check specifically for Telegram records
print("\n=== TELEGRAM RECORDS ===")
cur.execute("""
    SELECT id, user_id, model, 
           input_tokens, output_tokens, total_tokens, 
           created_at
    FROM token_usage 
    WHERE request_type = 'telegram'
    ORDER BY created_at DESC
""")
telegram_rows = cur.fetchall()
print(f"Total Telegram records: {len(telegram_rows)}")
for row in telegram_rows:
    print(f"ID: {row[0]} | User: {row[1]} | Model: {row[2]} | "
          f"I/O/T: {row[3]}/{row[4]}/{row[5]} | Time: {row[6]}")

# Check for the specific record mentioned (271/329/600)
print("\n=== SPECIFIC RECORD (271/329/600) ===")
cur.execute("""
    SELECT id, user_id, request_type, model, 
           input_tokens, output_tokens, total_tokens, 
           created_at, conversation_id
    FROM token_usage 
    WHERE input_tokens = 271 AND output_tokens = 329 AND total_tokens = 600
""")
specific = cur.fetchone()
if specific:
    print(f"FOUND: ID: {specific[0]} | User: {specific[1]} | Type: {specific[2]} | Model: {specific[3]}")
    print(f"       I/O/T: {specific[4]}/{specific[5]}/{specific[6]} | Time: {specific[7]} | Conv: {specific[8]}")
else:
    print("NOT FOUND")

# Check summary stats
print("\n=== SUMMARY BY REQUEST TYPE ===")
cur.execute("""
    SELECT request_type, 
           COUNT(*) as requests, 
           SUM(input_tokens) as input, 
           SUM(output_tokens) as output, 
           SUM(total_tokens) as total
    FROM token_usage 
    GROUP BY request_type
""")
summary = cur.fetchall()
for row in summary:
    print(f"{row[0]}: {row[1]} requests | I/O/T: {row[2]}/{row[3]}/{row[4]}")

cur.close()
conn.close()
