import os
import json
import psycopg2
from dotenv import load_dotenv
from collections import Counter

# load zmiennych z .env
load_dotenv()

def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST")
    )

def get_or_create_type(cur, type_name):
    if not type_name:
        return None
    cur.execute("""
        INSERT INTO silver_types (type_name) 
        VALUES (%s) 
        ON CONFLICT (type_name) DO NOTHING
        RETURNING type_id;
    """, (type_name,))
    result = cur.fetchone()
    if result:
        return result[0]
    cur.execute("SELECT type_id FROM silver_types WHERE type_name = %s", (type_name,))
    return cur.fetchone()[0]

def load_artist(cur, artist_name):
    name = artist_name if artist_name else "Unknown"
    cur.execute("""
        INSERT INTO silver_artists (artist_name) 
        VALUES (%s) 
        ON CONFLICT (artist_name) DO NOTHING
        RETURNING artist_id;
    """, (name,))
    result = cur.fetchone()
    if result:
        return result[0]
    cur.execute("SELECT artist_id FROM silver_artists WHERE artist_name = %s", (name,))
    return cur.fetchone()[0]

def load_set(cur, set_id_from_file, set_data):
    name = set_data.get('name', set_id_from_file.replace('-', ' ').capitalize())
    series = set_data.get('series', 'Unknown Series')
    printed_total = set_data.get('printedTotal')
    total = set_data.get('total')
    release_date = set_data.get('releaseDate')

    cur.execute("""
        INSERT INTO silver_sets (set_id, name, series, printed_total, total, release_date) 
        VALUES (%s, %s, %s, %s, %s, %s) 
        ON CONFLICT (set_id) DO UPDATE SET 
            name = EXCLUDED.name,
            release_date = EXCLUDED.release_date
        RETURNING set_id;
    """, (set_id_from_file, name, series, printed_total, total, release_date))
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

def load_card_details(cur, card_id, card_data):
    for t_name in card_data.get('types', []):
        t_id = get_or_create_type(cur, t_name)
        cur.execute("INSERT INTO silver_card_types (card_id, type_id) VALUES (%s, %s) ON CONFLICT DO NOTHING", (card_id, t_id))
    
    for weak in card_data.get('weaknesses', []):
        t_id = get_or_create_type(cur, weak.get('type'))
        cur.execute("INSERT INTO silver_card_weaknesses (card_id, type_id, value) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING", 
                    (card_id, t_id, weak.get('value')))

def load_attacks(cur, card_id, attacks_data):
    if not attacks_data:
        return
    for atk in attacks_data:
        cur.execute("""
            INSERT INTO silver_attacks (card_id, name, damage, description, converted_energy_cost)
            VALUES (%s, %s, %s, %s, %s) RETURNING attack_id;
        """, (card_id, atk.get('name'), atk.get('damage'), atk.get('text'), atk.get('convertedEnergyCost')))
        attack_id = cur.fetchone()[0]

        costs = Counter(atk.get('cost', []))
        for t_name, count in costs.items():
            t_id = get_or_create_type(cur, t_name)
            cur.execute("INSERT INTO silver_attack_costs (attack_id, type_id, count) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING", 
                        (attack_id, t_id, count))

def run_etl():
    conn = get_db_connection()
    cur = conn.cursor()
    
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    path = os.path.join(base_dir, 'data', 'bronze', 'cards')
    
    if not os.path.exists(path):
        print(f"!!! Error: Directory {path} missing !!!")
        return

    files = [f for f in os.listdir(path) if f.endswith('.json')]
    print(f"--- ETL Start (No Prices): {len(files)} sets ---")

    total_cards = 0

    for file in files:
        set_id = file.replace('.json', '')
        file_path = os.path.join(path, file)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                content = json.load(f)
                cards = content.get('data', []) if isinstance(content, dict) else content
                
                if not isinstance(cards, list) or not cards: continue

                s_id = load_set(cur, set_id, cards[0].get('set', {}))

                for card_data in cards:
                    c_id = card_data.get('id')
                    a_id = load_artist(cur, card_data.get('artist'))
                    
                    load_card(cur, card_data, a_id, s_id)
                    load_card_details(cur, c_id, card_data)
                    load_attacks(cur, c_id, card_data.get('attacks', []))
                    total_cards += 1

                conn.commit()
                print(f"Done: {set_id}")
            except Exception as e:
                print(f"!!! Exception in {file}: {e} !!!")
                conn.rollback()

    cur.close()
    conn.close()
    print(f"--- Finished: {total_cards} cards processed ---")

if __name__ == "__main__":
    run_etl()