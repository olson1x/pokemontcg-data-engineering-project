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
    
    print("--- Ładowanie wymiarów (Dimensions) ---")

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

    # load dim_types (NOWE - Słownik żywiołów)
    cur.execute("""
        INSERT INTO dim_types (type_name)
        SELECT DISTINCT type_name 
        FROM silver_types
        WHERE type_name IS NOT NULL 
          AND type_name NOT IN (SELECT type_name FROM dim_types);
    """)

    print("--- Ładowanie tabeli faktów (Fact Table) ---")

    # duplication avoidance
    cur.execute("TRUNCATE TABLE fact_cards RESTART IDENTITY;")

    # load fact_cards
    cur.execute("""
        INSERT INTO fact_cards (
            card_id, card_name, supertype, evolves_from, evolves_to,
            set_key, rarity_key, artist_key, 
            primary_type_key, weakness_type_key, resistance_type_key,
            weakness_value, resistance_value,
            hp_value, max_attack_damage, avg_attack_damage, energy_cost_total
        )
        WITH attack_stats AS (
            SELECT 
                card_id,
                -- REGEXP wycina wszystko co nie jest cyfrą, uwalniając wartości takie jak "50+" czy "10x"
                MAX(NULLIF(REGEXP_REPLACE(damage, '[^0-9]', '', 'g'), '')::INTEGER) AS max_attack_damage,
                ROUND(AVG(NULLIF(REGEXP_REPLACE(damage, '[^0-9]', '', 'g'), '')::DECIMAL), 2) AS avg_attack_damage
            FROM silver_attacks
            WHERE damage IS NOT NULL
            GROUP BY card_id
        ),
        cost_stats AS (
            SELECT 
                attack_id,
                SUM(count::INTEGER) AS attack_cost 
            FROM silver_attack_costs
            GROUP BY attack_id
        ),
        total_card_costs AS (
            SELECT 
                sa.card_id,
                SUM(cs.attack_cost) AS energy_cost_total 
            FROM silver_attacks sa
            JOIN cost_stats cs ON sa.attack_id = cs.attack_id
            GROUP BY sa.card_id
        ),
        -- Bezpieczne spłaszczenie słabości (bierzemy pierwszą, jeśli jest ich więcej)
        first_weakness AS (
            SELECT card_id, type_id, value
            FROM (
                SELECT card_id, type_id, value, 
                       ROW_NUMBER() OVER(PARTITION BY card_id ORDER BY type_id) as rn
                FROM silver_card_weaknesses
            ) w WHERE rn = 1
        ),
        -- Bezpieczne spłaszczenie odporności (bierzemy pierwszą)
        first_resistance AS (
            SELECT card_id, type_id, value
            FROM (
                SELECT card_id, type_id, value, 
                       ROW_NUMBER() OVER(PARTITION BY card_id ORDER BY type_id) as rn
                FROM silver_card_resistances
            ) r WHERE rn = 1
        )
        
        -- FINALNY SELECT
        SELECT 
            c.card_id,
            c.name,
            c.supertype,
            c.evolves_from,
            c.evolves_to,
            ds.set_key,
            dr.rarity_key,
            da.artist_key,
            dt_prim.type_key,
            dt_weak.type_key,
            dt_res.type_key,
            fw.value AS weakness_value,
            fr.value AS resistance_value,
            c.hp,
            atk.max_attack_damage,
            atk.avg_attack_damage,
            tcc.energy_cost_total
        FROM silver_cards c
        LEFT JOIN dim_sets ds ON c.set_id = ds.set_id
        LEFT JOIN dim_rarity dr ON c.rarity = dr.rarity_name
        LEFT JOIN silver_artists sa ON c.artist_id = sa.artist_id
        LEFT JOIN dim_artists da ON sa.artist_name = da.artist_name
        LEFT JOIN attack_stats atk ON c.card_id = atk.card_id
        LEFT JOIN total_card_costs tcc ON c.card_id = tcc.card_id
        
        -- Relacje do Typów (Żywiołów)
        LEFT JOIN silver_types st_prim ON c.type_id = st_prim.type_id
        LEFT JOIN dim_types dt_prim ON st_prim.type_name = dt_prim.type_name
        
        LEFT JOIN first_weakness fw ON c.card_id = fw.card_id
        LEFT JOIN silver_types st_weak ON fw.type_id = st_weak.type_id
        LEFT JOIN dim_types dt_weak ON st_weak.type_name = dt_weak.type_name
        
        LEFT JOIN first_resistance fr ON c.card_id = fr.card_id
        LEFT JOIN silver_types st_res ON fr.type_id = st_res.type_id
        LEFT JOIN dim_types dt_res ON st_res.type_name = dt_res.type_name;
    """)
    conn.commit()
    
    # insert check
    cur.execute("SELECT count(*) FROM fact_cards;")
    total_facts = cur.fetchone()[0]
    
    print(f"SUKCES! Załadowano {total_facts} wierszy do tabeli fact_cards.")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    run_gold_load()