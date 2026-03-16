import os
import json
import psycopg2
from dotenv import load_dotenv

load_dotenv()

# connection with db
def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST")
    )

def load_artist(cur, artist_name):
    name = artist_name if artist_name else "Unknown"
    cur.execute("""
        INSERT INTO silver_artists (artist_name) 
        VALUES (%s) 
        ON CONFLICT (artist_name) DO UPDATE SET artist_name = EXCLUDED.artist_name
        RETURNING artist_id;
    """, (name,))
    return cur.fetchone()[0]

def load_set(cur, set_data):
    if not set_data or not isinstance(set_data, dict):
        params = ("unknown", "Unknown Set", "Unknown", None)
    else:
        params = (
            set_data.get('id', 'unknown'),
            set_data.get('name', 'Unknown Set'),
            set_data.get('series', 'Unknown'),
            set_data.get('releaseDate')
        )

    cur.execute("""
        INSERT INTO silver_sets (set_id, name, series, release_date) 
        VALUES (%s, %s, %s, %s) 
        ON CONFLICT (set_id) DO UPDATE SET 
            name = EXCLUDED.name,
            series = EXCLUDED.series,
            release_date = EXCLUDED.release_date
        RETURNING set_id;
    """, params)
    return cur.fetchone()[0]

def load_card(cur, card_data, artist_id, set_id):
    hp_raw = card_data.get('hp')
    try:
        hp_value = int(hp_raw) if hp_raw else None
    except (ValueError, TypeError):
        hp_value = None

    cur.execute("""
        INSERT INTO silver_cards (
            card_id, name, supertype, hp, artist_id, set_id, rarity, flavor_text
        ) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s) 
        ON CONFLICT (card_id) DO UPDATE SET 
            name = EXCLUDED.name,
            hp = EXCLUDED.hp,
            rarity = EXCLUDED.rarity
        RETURNING card_id;
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
    return cur.fetchone()[0]

def run_etl():
    conn = get_db_connection()
    cur = conn.cursor()
    
    path = 'data/bronze/cards'
    if not os.path.exists(path):
        print(f"Error: Path {path} not found")
        return

    files = [f for f in os.listdir(path) if f.endswith('.json')]

    for file in files:
        with open(os.path.join(path, file), 'r', encoding='utf-8') as f:
            try:
                content = json.load(f)
                cards = content.get('data', []) if isinstance(content, dict) else content
                
                if not isinstance(cards, list):
                    continue

                print(f"Processing {file} ({len(cards)} cards)")

                for card_data in cards:
                    if not card_data: continue
                    a_id = load_artist(cur, card_data.get('artist'))
                    s_id = load_set(cur, card_data.get('set'))
                    load_card(cur, card_data, a_id, s_id)
                
                conn.commit()
                
            except Exception as e:
                print(f"Error processing {file}: {e}")
                conn.rollback()

    cur.close()
    conn.close()
    print("ETL job finished.")

if __name__ == "__main__":
    run_etl()