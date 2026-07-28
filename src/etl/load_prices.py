import os
import time
import psycopg2
from dotenv import load_dotenv

# path import
from src.config import MARKET_PRICES_FILE

# load env
load_dotenv()

def get_db_connection():
    """connect to postgres database."""
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST")
    )

def load_market_prices():
    """load price history from csv using fast bulk copy."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
    except Exception as e:
        print(f"db connection error: {e}")
        return
    
    try:
        # exist check
        if not MARKET_PRICES_FILE.exists():
            print(f"error: missing file at {MARKET_PRICES_FILE}")
            return
        
        print("starting bulk load...")
        
        start_time = time.time()
        
        # clear table to avoid duplicates on rerun
        cur.execute("TRUNCATE TABLE silver_prices;")
        
        with open(MARKET_PRICES_FILE, 'r', encoding='utf-8') as f:
            copy_sql = """
                COPY silver_prices (card_id, set_id, date, market_price_usd) 
                FROM STDIN WITH CSV HEADER DELIMITER ','
            """
            cur.copy_expert(sql=copy_sql, file=f)
            
        conn.commit()
        
        end_time = time.time()
        print(f"done: loaded in {round(end_time - start_time, 2)}s")
        
    except Exception as e:
        print(f"error: {e}")
        conn.rollback()
    finally:
        if 'cur' in locals() and cur:
            cur.close()
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    load_market_prices()