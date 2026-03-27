import os
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

def run_gold_load():
    conn = get_db_connection()
    cur = conn.cursor()
    
    print("Loading dim_tables")

    # load dim_sets
    cur.execute("""
        INSERT INTO dim_sets (set_id, set_name, series, release_date, total_cards_in_set)
        SELECT DISTINCT set_id, name, series, release_date, printed_total 
        FROM silver_sets
        WHERE set_id NOT IN (SELECT set_id FROM dim_sets);
    """)

    # load dim_rarity
    cur.execute("""
        INSERT INTO dim_rarity (rarity_name)
        SELECT DISTINCT rarity 
        FROM silver_cards
        WHERE rarity IS NOT NULL 
          AND rarity NOT IN (SELECT rarity_name FROM dim_rarity);
    """)

    print("loading fact_cards")

    # duplication avoidance
    cur.execute("TRUNCATE TABLE fact_cards RESTART IDENTITY;")

    # load fact_cards
    cur.execute("""
        INSERT INTO fact_cards (
            card_id, set_key, rarity_key, hp_value, 
            market_price
        )
        SELECT 
            c.card_id,
            ds.set_key,
            dr.rarity_key,
            c.hp,  -- TUTAJ ZMIANA: bierzemy czyste c.hp, bez żadnych kombinacji
            c.market_price
        FROM silver_cards c
        LEFT JOIN dim_sets ds ON c.set_id = ds.set_id
        LEFT JOIN dim_rarity dr ON c.rarity = dr.rarity_name;
    """)
    conn.commit()
    
    # insert check
    cur.execute("SELECT count(*) FROM fact_cards;")
    total_facts = cur.fetchone()[0]
    
    print(f"Success! Inserted {total_facts} rows into fact_cards.")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    run_gold_load()