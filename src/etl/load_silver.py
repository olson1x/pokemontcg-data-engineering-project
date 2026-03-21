import os
import json
import psycopg2
from dotenv import load_dotenv

# load zmiennych z .env
load_dotenv()

def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST")
    )

def load_artist(cur, artist_name):
    name = artist_name if artist_name else "Unknown"

    # artist ingest z obsługa duplikatów
    cur.execute("""
        INSERT INTO silver_artists (artist_name) 
        VALUES (%s) 
        ON CONFLICT (artist_name) DO NOTHING
        RETURNING artist_id;
    """, (name,))
    
    result = cur.fetchone()
    if result:
        return result[0]
    
    # jeśli artist exists, dociągamy id
    cur.execute("SELECT artist_id FROM silver_artists WHERE artist_name = %s", (name,))
    return cur.fetchone()[0]

def load_set(cur, set_id_from_file):
    # formatowanie nazwy z filename
    clean_name = set_id_from_file.replace('-', ' ').capitalize()
    
    cur.execute("""
        INSERT INTO silver_sets (set_id, name, series) 
        VALUES (%s, %s, %s) 
        ON CONFLICT (set_id) DO UPDATE SET name = EXCLUDED.name
        RETURNING set_id;
    """, (set_id_from_file, clean_name, "Unknown Series"))
    return cur.fetchone()[0]

def load_card(cur, card_data, artist_id, set_id):
    # data cleaning dla HP pola
    hp_raw = card_data.get('hp')
    try:
        hp_value = int(hp_raw) if hp_raw else None
    except (ValueError, TypeError):
        hp_value = None

    # persistence kart w db
    cur.execute("""
        INSERT INTO silver_cards (
            card_id, name, supertype, hp, artist_id, set_id, rarity, flavor_text
        ) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s) 
        ON CONFLICT (card_id) DO UPDATE SET 
            name = EXCLUDED.name,
            hp = EXCLUDED.hp,
            rarity = EXCLUDED.rarity;
    """, (
        card_data.get('id'), 
        card_data.get('name', 'Unknown Card'), 
        card_data.get('supertype'), 
        hp_value, 
        artist_id, 
        set_id, 
        card_data.get('rarity', 'Unknown'),
        card_data.get('flavorText')
    ))

def run_etl():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # path resolve dla warstwy bronze
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    path = os.path.join(base_dir, 'data', 'bronze', 'cards')
    
    if not os.path.exists(path):
        print(f"!!! Error: Directory {path} missing !!!")
        return

    files = [f for f in os.listdir(path) if f.endswith('.json')]
    print(f"--- ETL Start: {len(files)} sets detected ---")

    total_cards = 0

    for file in files:
        set_id = file.replace('.json', '')
        file_path = os.path.join(path, file)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                content = json.load(f)
                cards = content.get('data', []) if isinstance(content, dict) else content
                
                if not isinstance(cards, list): 
                    continue

                # batch processing per file
                s_id = load_set(cur, set_id)

                for card_data in cards:
                    a_id = load_artist(cur, card_data.get('artist'))
                    load_card(cur, card_data, a_id, s_id)
                    total_cards += 1

                # persistence per set
                conn.commit()
                print(f"Done: {set_id}")
                
            except Exception as e:
                print(f"!!! Exception in {file}: {e} !!!")
                conn.rollback()

    cur.close()
    conn.close()
    print(f"--- Finished: {total_cards} cards in DB ---")

if __name__ == "__main__":
    run_etl()