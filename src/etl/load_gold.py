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
    
    print("Loading dim_tables...")

    # load dim_sets
    cur.execute("""
        INSERT INTO dim_sets (set_id, set_name, series, release_date, release_year, total_cards_in_set)
        SELECT DISTINCT 
            set_id, 
            name, 
            series, 
            release_date, 
            EXTRACT(YEAR FROM release_date)::INTEGER, 
            printed_total 
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

    # load dim_artists
    cur.execute("""
        INSERT INTO dim_artists (artist_name)
        SELECT DISTINCT artist_name 
        FROM silver_artists
        WHERE artist_name IS NOT NULL 
          AND artist_name NOT IN (SELECT artist_name FROM dim_artists);
    """)

    print("Loading fact_cards...")

    # duplication avoidance
    cur.execute("TRUNCATE TABLE fact_cards RESTART IDENTITY;")

    # load fact_cards
    cur.execute("""
        INSERT INTO fact_cards (
            card_id, set_key, rarity_key, artist_key, hp_value, 
            max_attack_damage, avg_attack_damage, energy_cost_total, market_price
        )
        WITH attack_stats AS (
            SELECT 
                card_id,
                MAX(damage::INTEGER) AS max_attack_damage,
                ROUND(AVG(damage::DECIMAL), 2) AS avg_attack_damage
            FROM silver_attacks
            WHERE damage IS NOT NULL AND damage ~ '^[0-9]+$' -- proste zabezpieczenie rzutowania
            GROUP BY card_id
        ),
        cost_stats AS (
            SELECT 
                attack_id,
                SUM(count::INTEGER) AS attack_cost -- sumujemy koszty dla pojedynczego ataku
            FROM silver_attack_costs
            GROUP BY attack_id
        ),
        total_card_costs AS (
            SELECT 
                sa.card_id,
                SUM(cs.attack_cost) AS energy_cost_total -- sumujemy koszty wszystkich ataków karty
            FROM silver_attacks sa
            JOIN cost_stats cs ON sa.attack_id = cs.attack_id
            GROUP BY sa.card_id
        )
        SELECT 
            c.card_id,
            ds.set_key,
            dr.rarity_key,
            da.artist_key,
            c.hp,
            atk.max_attack_damage,
            atk.avg_attack_damage,
            tcc.energy_cost_total,
            c.market_price
        FROM silver_cards c
        LEFT JOIN dim_sets ds ON c.set_id = ds.set_id
        LEFT JOIN dim_rarity dr ON c.rarity = dr.rarity_name
        LEFT JOIN silver_artists sa ON c.artist_id = sa.artist_id
        LEFT JOIN dim_artists da ON sa.artist_name = da.artist_name
        LEFT JOIN attack_stats atk ON c.card_id = atk.card_id
        LEFT JOIN total_card_costs tcc ON c.card_id = tcc.card_id;
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