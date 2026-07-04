import os
import psycopg2
from dotenv import load_dotenv

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
    
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    prices_path = os.path.join(base_dir, 'data', 'bronze', 'prices', 'market_prices.csv')
    
    if not os.path.exists(prices_path):
        print(f"error: missing prices file at {prices_path}")
        return
    
    print("starting bulk load for prices...")
    
    # clear table to avoid duplicates on rerun
    cur.execute("TRUNCATE TABLE silver_prices;")
    
    # fast copy directly to postgres engine
    with open(prices_path, 'r', encoding='utf-8') as f:
        copy_sql = """
            COPY silver_prices (card_id, set_id, date, market_price_usd) 
            FROM STDIN WITH CSV HEADER DELIMITER ','
        """
        cur.copy_expert(sql=copy_sql, file=f)
        
    conn.commit()
    cur.close()
    conn.close()
    
    print("finished loading market prices.")

if __name__ == "__main__":
    load_market_prices()