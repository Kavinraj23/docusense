import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()  # Loads the .env file

try:
    conn = psycopg2.connect(
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT")
    )
    print("PostgreSQL connection successful")
    conn.close()
except Exception as e:
    print("PostgreSQL connection failed")
    print(e)