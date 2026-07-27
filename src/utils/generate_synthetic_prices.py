import os
import csv
import psycopg2
import random
from datetime import date, timedelta
from dotenv import load_dotenv

from src.config import MARKET_PRICES_FILE

load_dotenv()

def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST")
    )

def generate_market_data():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # pobranie ID karty, ID setu i nazwy z bazy
    cur.execute("SELECT card_id, set_id, name FROM silver_cards;")
    db_cards = cur.fetchall()
    
    cur.close()
    conn.close()
    
    total_cards = len(db_cards)
    if total_cards == 0:
        print("Błąd: silver_cards table is empty, please load JSONs.")
        return

    print(f" {total_cards} cards found")

    # konfiguracja okresu (100 dni)
    days_history = 100
    start_date = date.today() - timedelta(days=days_history)
    total_expected_rows = total_cards * days_history

    # tworzenie folderów docelowych przy użyciu pathlib
    MARKET_PRICES_FILE.parent.mkdir(parents=True, exist_ok=True)

    print(f"generating {total_expected_rows} prices and saving into {MARKET_PRICES_FILE}...")
    
    headers = ['card_id', 'set_id', 'date', 'market_price_usd']
    
    generated_count = 0
    with open(MARKET_PRICES_FILE, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        
        for card_id, set_id, name in db_cards:
            # setting up a random price
            current_price = round(random.uniform(0.50, 150.00), 2)
            
            for day_offset in range(days_history):
                current_date = start_date + timedelta(days=day_offset)
                
                writer.writerow([card_id, set_id, current_date.isoformat(), round(current_price, 2)])
                generated_count += 1
                
                # price fluctuations simulation
                fluctuation = random.uniform(0.95, 1.05)
                current_price = current_price * fluctuation
                
                if current_price < 0.01:
                    current_price = 0.01
            
            if generated_count % 100000 == 0:
                print(f"{generated_count} / {total_expected_rows} rows generated")

    print(f"{generated_count} prices saved")

if __name__ == "__main__":
    generate_market_data()