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
    conn = get_db_connection()
    cur = conn.cursor()
    
    # exist check
    if not MARKET_PRICES_FILE.exists():
        print(f"error: missing prices file at {MARKET_PRICES_FILE}")
        return
    
    print("starting bulk load for prices...")
    
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
    cur.close()
    conn.close()
    
    end_time = time.time()
    print(f"finished loading market prices in {round(end_time - start_time, 2)} seconds.")

if __name__ == "__main__":
    load_market_prices()