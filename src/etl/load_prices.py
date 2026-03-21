import os
import csv
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST")
    )

def run_prices_load():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # set path
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    csv_path = os.path.join(base_dir, 'data', 'bronze', 'prices', 'market_prices.csv')
    
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        return

    print("updating prices...")
    success_count = 0

    with open(csv_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cur.execute("""
                UPDATE silver_cards 
                SET market_price = %s 
                WHERE card_id = %s;
            """, (row['market_price_usd'], row['card_id']))
            
            if cur.rowcount > 0:
                success_count += 1

    conn.commit()
    
    print(f"updated: {success_count} records.")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    run_prices_load()