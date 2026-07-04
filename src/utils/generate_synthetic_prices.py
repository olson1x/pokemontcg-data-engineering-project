import os
import csv
import psycopg2
import random
from datetime import date, timedelta
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

    # Konfiguracja okresu (100 dni)
    days_history = 100
    start_date = date.today() - timedelta(days=days_history)
    total_expected_rows = total_cards * days_history

    # generowanie cen i save do CSV
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    output_path = os.path.join(base_dir, 'data', 'bronze', 'prices', 'market_prices.csv')
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    print(f"Generuję {total_expected_rows} cen historycznych i zapisuję do {output_path}...")
    
    headers = ['card_id', 'set_id', 'date', 'market_price_usd']
    
    generated_count = 0
    with open(output_path, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        
        for card_id, set_id, name in db_cards:
            # Losujemy cenę początkową dla karty z pierwszego dnia (od 0.50$ do 150.00$)
            current_price = round(random.uniform(0.50, 150.00), 2)
            
            for day_offset in range(days_history):
                current_date = start_date + timedelta(days=day_offset)
                
                # Zapisujemy cenę z danego dnia
                writer.writerow([card_id, set_id, current_date.isoformat(), round(current_price, 2)])
                generated_count += 1
                
                # Symulacja giełdy: zmiana ceny na kolejny dzień (od -5% do +5%)
                fluctuation = random.uniform(0.95, 1.05)
                current_price = current_price * fluctuation
                
                # Zabezpieczenie przed ujemnymi cenami lub zerem
                if current_price < 0.01:
                    current_price = 0.01
            
            # logowanie co 100 000 wygenerowanych wierszy, żeby nie zaciąć konsoli
            if generated_count % 100000 == 0:
                print(f"... wygenerowano {generated_count} / {total_expected_rows} wierszy ...")

    print(f"Sukces! Zapisano {generated_count} rekordów cenowych.")

if __name__ == "__main__":
    generate_market_data()