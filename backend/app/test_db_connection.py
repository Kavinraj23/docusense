#!/usr/bin/env python3
"""
Test script to verify database connection locally
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import sys

def test_database_connection():
    """Test the database connection using environment variables"""
    
    # Load environment variables
    load_dotenv()
    
    # Get DATABASE_URL from environment
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        print("Make sure you have a .env file with DATABASE_URL set")
        return False
    
    print(f"🔗 Testing connection to: {database_url.split('@')[1] if '@' in database_url else 'Unknown'}")
    
    try:
        # Create engine
        engine = create_engine(
            database_url,
            pool_pre_ping=True,
            pool_recycle=300
        )
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            
            if row and row[0] == 1:
                print("✅ Database connection successful!")
                
                # Test a few more queries
                print("\n🔍 Testing additional queries...")
                
                # Check if tables exist
                result = conn.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    ORDER BY table_name
                """))
                tables = [row[0] for row in result.fetchall()]
                
                if tables:
                    print(f"✅ Found {len(tables)} tables: {', '.join(tables)}")
                else:
                    print("⚠️  No tables found in public schema")
                
                # Check database version
                result = conn.execute(text("SELECT version()"))
                version = result.fetchone()[0]
                print(f"📊 Database version: {version.split(',')[0]}")
                
                return True
            else:
                print("❌ Connection test failed - unexpected result")
                return False
                
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print(f"Error type: {type(e).__name__}")
        return False

def test_individual_env_vars():
    """Test connection using individual environment variables"""
    print("\n🔧 Testing with individual environment variables...")
    
    db_name = os.getenv("POSTGRES_DB")
    db_user = os.getenv("POSTGRES_USER")
    db_password = os.getenv("POSTGRES_PASSWORD")
    db_host = os.getenv("POSTGRES_HOST")
    db_port = os.getenv("POSTGRES_PORT")
    
    if all([db_name, db_user, db_password, db_host, db_port]):
        database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        print(f"🔗 Testing local connection to: {db_host}:{db_port}/{db_name}")
        
        try:
            engine = create_engine(database_url, pool_pre_ping=True)
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1 as test"))
                if result.fetchone()[0] == 1:
                    print("✅ Local database connection successful!")
                    return True
        except Exception as e:
            print(f"❌ Local database connection failed: {e}")
    else:
        print("⚠️  Not all local database environment variables are set")
    
    return False

if __name__ == "__main__":
    print("🚀 Database Connection Test Script")
    print("=" * 40)
    
    # Test DATABASE_URL first
    success = test_database_connection()
    
    if not success:
        # Fallback to individual variables
        test_individual_env_vars()
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 Database connection test completed successfully!")
        sys.exit(0)
    else:
        print("💥 Database connection test failed!")
        sys.exit(1) 