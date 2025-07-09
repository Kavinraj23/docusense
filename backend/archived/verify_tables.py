# Create verify_tables.py
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))

try:
    with engine.connect() as conn:
        # Check if tables exist
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """))
        tables = [row[0] for row in result.fetchall()]
        print(f'✅ Tables in Supabase: {tables}')
        
        # Check specific tables we expect
        expected_tables = ['users', 'syllabi', 'google_calendar_credentials', 'oauth_states']
        for table in expected_tables:
            if table in tables:
                print(f'✅ {table} table exists')
            else:
                print(f'❌ {table} table missing')
                
except Exception as e:
    print(f'❌ Error: {e}')