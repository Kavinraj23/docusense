from sqlalchemy import create_engine
from db.session import DATABASE_URL

def test_connection():
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as connection:
            print("Successfully connected to the database!")
            return True
    except Exception as e:
        print(f"Failed to connect to the database. Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_connection()
