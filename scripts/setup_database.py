import psycopg2
import psycopg2.errors
import os
from dotenv import load_dotenv

# Load environment variables from your .env file
load_dotenv()

DB_CONFIG = {
    "dbname": os.getenv("dbname"),
    "user": os.getenv("user"),
    "password": os.getenv("password"),
    "host": os.getenv("host"),
    "port": os.getenv("port"),
    "sslmode": "require"
}

def create_tables():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        with open("./sql/database_schema.sql", "r") as file:
            schema_sql = file.read()
            try:
                cursor.execute(schema_sql)
            except psycopg2.errors.DuplicateTable:
                print("Tables already exist, continuing anyway.")
                conn.rollback()

        conn.commit()
        cursor.close()
        conn.close()
        print("Database and tables created successfully (or already exist).")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    create_tables()
