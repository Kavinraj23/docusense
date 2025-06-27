import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
print(f'Testing connection...')
engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as conn:
        result = conn.execute(text('SELECT version()'))
        print('✅ Database connection successful!')
        print(f'PostgreSQL version: {result.fetchone()[0]}')
except Exception as e:
    print(f'❌ Database connection failed: {e}')