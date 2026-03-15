import os
import psycopg2
from dotenv import load_dotenv

# Load database credentials from .env
load_dotenv()

def get_db_connection():
    """Establishes a connection session with the PostgreSQL instance."""
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST")
    )

def load_artist(cur, artist_name):
    """
    Performs an UPSERT operation on silver_artists table.
    Returns the primary key (artist_id) for relational mapping.
    """
    if not artist_name:
        artist_name = "Unknown"
        
    cur.execute("""
        INSERT INTO silver_artists (name) 
        VALUES (%s) 
        ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name
        RETURNING artist_id;
    """, (artist_name,))
    return cur.fetchone()[0]