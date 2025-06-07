from app.db.session import engine, Base
from app.db.models import *  # Import all models (including Document)
from sqlalchemy.exc import SQLAlchemyError

def init_db():
    try:
        Base.metadata.drop_all(bind=engine) # Drop all tables first
        Base.metadata.create_all(bind=engine)  # Create tables for all models
        print("Tables created successfully.")
    except SQLAlchemyError as e:
        print(f"Error creating tables: {e}")

if __name__ == "__main__":
    init_db()
