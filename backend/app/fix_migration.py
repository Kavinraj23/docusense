#!/usr/bin/env python3
"""
Script to fix the migration issue by dropping the user_id column if it exists.
Run this before recreating the migration.
"""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_database_url():
    """Get database URL from environment or use default."""
    # You can set DATABASE_URL in your .env file
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        # Default to local PostgreSQL
        database_url = "postgresql://postgres:password@localhost:5432/study_snap"
        print(f"Using default database URL: {database_url}")
        print("If this is wrong, set DATABASE_URL in your .env file")
    
    return database_url

def drop_user_id_column():
    """Drop the user_id column if it exists."""
    try:
        # Create engine
        engine = create_engine(get_database_url())
        
        with engine.connect() as conn:
            # Check if user_id column exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'syllabi' AND column_name = 'user_id'
            """))
            
            if result.fetchone():
                print("Found user_id column. Dropping it...")
                conn.execute(text("ALTER TABLE syllabi DROP COLUMN user_id"))
                conn.commit()
                print("✅ Successfully dropped user_id column")
            else:
                print("✅ user_id column doesn't exist (good!)")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nYou may need to:")
        print("1. Check your database connection")
        print("2. Make sure you're using the right database")
        print("3. Run this script from the backend/app directory")
        return False
    
    return True

if __name__ == "__main__":
    print("🔧 Fixing migration issue...")
    print("This will drop the user_id column if it exists.")
    print("Then you can recreate it with the correct UUID type.\n")
    
    success = drop_user_id_column()
    
    if success:
        print("\n🎉 Done! Now you can:")
        print("1. Delete the broken migration file")
        print("2. Run: alembic revision --autogenerate -m 'Add user_id as UUID to Syllabus model'")
        print("3. Run: alembic upgrade head")
    else:
        print("\n❌ Failed to fix the issue. Please check the error above.") 