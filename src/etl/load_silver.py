import os
import json
import time
import psycopg2
from dotenv import load_dotenv
from collections import Counter

from src.config import ALL_SETS_FILE, CARDS_DIR

# load env variables
load_dotenv()

def get_db_connection():
    """connect to postgres database."""
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST")
    )

def get_or_create_type(cur, type_name):
    """get or create type id."""
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

def get_or_create_subtype(cur, subtype_name):
    """get or create subtype id."""
    if not subtype_name:
        return None
    cur.execute("""
        INSERT INTO silver_subtypes (subtype_name) 
        VALUES (%s) 
        ON CONFLICT (subtype_name) DO NOTHING
        RETURNING subtype_id;
    """, (subtype_name,))
    result = cur.fetchone()
    if result:
        return result[0]
    cur.execute("SELECT subtype_id FROM silver_subtypes WHERE subtype_name = %s", (subtype_name,))
    return cur.fetchone()[0]

def load_artist(cur, artist_name):
    """get or create artist id."""
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

def load_all_sets(cur):
    """load set stats from json."""
    if not ALL_SETS_FILE.exists():
        print(f"error: missing sets file at {ALL_SETS_FILE}")
        return

    with open(ALL_SETS_FILE, 'r', encoding='utf-8') as f:
        content = json.load(f)
        sets_data = content.get('data', [])
        
        for s in sets_data:
            cur.execute("""
                INSERT INTO silver_sets (set_id, name, series, printed_total, total, release_date) 
                VALUES (%s, %s, %s, %s, %s, %s) 
                ON CONFLICT (set_id) DO UPDATE SET 
                    name = EXCLUDED.name,
                    series = EXCLUDED.series,
                    printed_total = EXCLUDED.printed_total,
                    total = EXCLUDED.total,
                    release_date = EXCLUDED.release_date;
            """, (
                s.get('id'),
                s.get('name', 'Unknown'),
                s.get('series', 'Unknown'),
                s.get('printedTotal'),
                s.get('total'),
                s.get('releaseDate')
            ))
    print(f"loaded {len(sets_data)} sets.")

def load_card(cur, card_data, artist_id, set_id):
    """load main card data."""
    hp_raw = card_data.get('hp')
    try:
        hp_value = int(hp_raw) if hp_raw else None
    except (ValueError, TypeError):
        hp_value = None

    evolves_from = card_data.get('evolvesFrom')
    evolves_to_raw = card_data.get('evolvesTo')
    evolves_to = ", ".join(evolves_to_raw) if isinstance(evolves_to_raw, list) else None

    cur.execute("""
        INSERT INTO silver_cards (
            card_id, name, supertype, hp, rarity, artist_id, set_id, evolves_from, evolves_to
        ) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) 
        ON CONFLICT (card_id) DO UPDATE SET 
            name = EXCLUDED.name,
            supertype = EXCLUDED.supertype,
            hp = EXCLUDED.hp,
            rarity = EXCLUDED.rarity,
            evolves_from = EXCLUDED.evolves_from,
            evolves_to = EXCLUDED.evolves_to;
    """, (
        card_data.get('id'), 
        card_data.get('name', 'Unknown Card'), 
        card_data.get('supertype'), 
        hp_value, 
        card_data.get('rarity', 'Unknown'),
        artist_id, 
        set_id,
        evolves_from,
        evolves_to
    ))

def load_card_types_and_subtypes(cur, card_id, card_data):
    """populate bridge tables for types and subtypes."""
    for t_name in card_data.get('types', []):
        t_id = get_or_create_type(cur, t_name)
        cur.execute("""
            INSERT INTO silver_card_types (card_id, type_id)
            VALUES (%s, %s) ON CONFLICT DO NOTHING
        """, (card_id, t_id))

    for s_name in card_data.get('subtypes', []):
        s_id = get_or_create_subtype(cur, s_name)
        cur.execute("""
            INSERT INTO silver_card_subtypes (card_id, subtype_id)
            VALUES (%s, %s) ON CONFLICT DO NOTHING
        """, (card_id, s_id))

def load_weaknesses_and_resistances(cur, card_id, card_data):
    """populate weaknesses and resistances."""
    for weak in card_data.get('weaknesses', []):
        t_id = get_or_create_type(cur, weak.get('type'))
        cur.execute("""
            INSERT INTO silver_card_weaknesses (card_id, type_id, value) 
            VALUES (%s, %s, %s) ON CONFLICT DO NOTHING
        """, (card_id, t_id, weak.get('value')))
        
    for res in card_data.get('resistances', []):
        t_id = get_or_create_type(cur, res.get('type'))
        cur.execute("""
            INSERT INTO silver_card_resistances (card_id, type_id, value) 
            VALUES (%s, %s, %s) ON CONFLICT DO NOTHING
        """, (card_id, t_id, res.get('value')))

def load_attacks(cur, card_id, attacks_data):
    """load attacks and energy costs."""
    if not attacks_data:
        return
    for atk in attacks_data:
        cur.execute("""
            INSERT INTO silver_attacks (card_id, name, damage, converted_energy_cost)
            VALUES (%s, %s, %s, %s) RETURNING attack_id;
        """, (
            card_id, 
            atk.get('name'), 
            atk.get('damage'), 
            atk.get('convertedEnergyCost')
        ))
        attack_id = cur.fetchone()[0]

        costs = Counter(atk.get('cost', []))
        for t_name, count in costs.items():
            t_id = get_or_create_type(cur, t_name)
            cur.execute("""
                INSERT INTO silver_attack_costs (attack_id, type_id, count) 
                VALUES (%s, %s, %s) ON CONFLICT DO NOTHING
            """, (attack_id, t_id, count))

def run_etl():
    """main etl process for static card data."""
    start_time = time.time()
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # ładujemy sety 
    load_all_sets(cur)
    conn.commit()

    if not CARDS_DIR.exists():
        print(f"error: missing cards directory at {CARDS_DIR}")
        return

    # używamy glob z pathlib do pobrania listy wszystkich plików .json
    files = list(CARDS_DIR.glob('*.json'))
    print(f"starting etl: {len(files)} files to process.")

    total_cards = 0

    for file_path in files:
        # wyciągamy nazwę pliku bez rozszerzenia .json używając właściwości .stem
        set_id = file_path.stem
        
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                content = json.load(f)
                cards = content.get('data', []) if isinstance(content, dict) else content
                
                if not isinstance(cards, list) or not cards: 
                    continue

                for card_data in cards:
                    c_id = card_data.get('id')
                    a_id = load_artist(cur, card_data.get('artist'))
                    
                    load_card(cur, card_data, a_id, set_id)
                    load_card_types_and_subtypes(cur, c_id, card_data)
                    load_weaknesses_and_resistances(cur, c_id, card_data)
                    load_attacks(cur, c_id, card_data.get('attacks', []))
                    total_cards += 1

                conn.commit()
                print(f"processed set: {set_id}")
            except Exception as e:
                print(f"error processing file {file_path.name}: {e}")
                conn.rollback()

    cur.close()
    conn.close()
    
    end_time = time.time()
    print(f"finished in {round(end_time - start_time, 2)} seconds. loaded {total_cards} cards.")

if __name__ == "__main__":
    run_etl()