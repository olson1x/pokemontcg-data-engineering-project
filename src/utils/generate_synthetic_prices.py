import os
import csv
import psycopg2
import random
from dotenv import load_dotenv

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
        print("Błąd: Twoja tabela silver_cards jest pusta! Najpierw załaduj JSONy.")
        return

    print(f"Znaleziono {total_cards} kart w bazie.")

    # generowanie cen i save do CSV
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    output_path = os.path.join(base_dir, 'data', 'bronze', 'prices', 'market_prices.csv')
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    print(f"Generuję ceny i zapisuję do {output_path}...")
    
    headers = ['card_id', 'set_id', 'market_price_usd']
    
    generated_count = 0
    with open(output_path, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        
        for card_id, set_id, name in db_cards:
            price = round(random.uniform(0.50, 150.00), 2)
            
            # zapis rekordów
            writer.writerow([card_id, set_id, price])
            generated_count += 1
            
            # log
            if generated_count % 5000 == 0:
                print(f"... {generated_count}/{total_cards} generated ...")

    print(f"{generated_count} succeded.")

if __name__ == "__main__":
    generate_market_data()