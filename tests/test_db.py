import psycopg2
from psycopg2.extras import RealDictCursor

try:
    conn = psycopg2.connect(
        host="localhost",
        port="5432",
        user="trantor",
        password="trantor_pass",
        database="trantor_db"
    )
    
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT version();")
        result = cur.fetchone()
        print("✅ Database connected successfully!")
        print(f"PostgreSQL version: {result['version']}")
        
        # Test pgvector extension
        cur.execute("SELECT * FROM pg_extension WHERE extname = 'vector';")
        if cur.fetchone():
            print("✅ pgvector extension is active")
        else:
            print("❌ pgvector extension not found")
            
    conn.close()
    
except Exception as e:
    print(f"❌ Database connection failed: {e}")