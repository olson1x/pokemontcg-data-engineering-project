import os
import time
import psycopg2
from dotenv import load_dotenv

# load env
load_dotenv()

def get_db_connection():
    """connect to postgres database."""
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST")
    )

def load_gold_layer():
    """transform silver tables into gold star schema with bridge tables."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
    except Exception as e:
        print(f"db connection error: {e}")
        return
        
    try:
        print("starting gold layer...")
        start_time = time.time()
        
        cur.execute("truncate table fact_prices, fact_card_metrics, bridge_card_types, bridge_card_subtypes cascade;")
        
        print("loading: dim_sets")
        cur.execute("""
            insert into dim_sets (set_id, set_name, series, release_date, release_year, total_cards_in_set)
            select 
                set_id, name, series, release_date, 
                extract(year from release_date)::int, total
            from silver_sets
            on conflict (set_id) do nothing;
        """)
        
        print("loading: dim_cards")
        cur.execute("""
            insert into dim_cards (card_id, card_name, supertype, rarity, hp_value, artist_name, evolves_from, evolves_to)
            select 
                c.card_id, c.name, c.supertype, c.rarity, c.hp,
                a.artist_name, c.evolves_from, c.evolves_to
            from silver_cards c
            left join silver_artists a on c.artist_id = a.artist_id
            on conflict (card_id) do nothing;
        """)

        print("loading: dim_types & dim_subtypes")
        cur.execute("""
            insert into dim_types (type_name)
            select type_name from silver_types
            on conflict (type_name) do nothing;
        """)
        
        cur.execute("""
            insert into dim_subtypes (subtype_name)
            select subtype_name from silver_subtypes
            on conflict (subtype_name) do nothing;
        """)

        print("loading: bridge tables")
        cur.execute("""
            insert into bridge_card_types (card_key, type_key)
            select dc.card_key, dt.type_key
            from silver_card_types sct
            join dim_cards dc on sct.card_id = dc.card_id
            join silver_types st on sct.type_id = st.type_id
            join dim_types dt on st.type_name = dt.type_name
            on conflict do nothing;
        """)

        cur.execute("""
            insert into bridge_card_subtypes (card_key, subtype_key)
            select dc.card_key, dst.subtype_key
            from silver_card_subtypes scst
            join dim_cards dc on scst.card_id = dc.card_id
            join silver_subtypes sst on scst.subtype_id = sst.subtype_id
            join dim_subtypes dst on sst.subtype_name = dst.subtype_name
            on conflict do nothing;
        """)
        
        print("loading: dim_date")
        cur.execute("""
            insert into dim_date (date_key, full_date, year, month, day, day_of_week)
            select distinct
                to_char(date, 'YYYYMMDD')::integer,
                date,
                extract(year from date)::int,
                extract(month from date)::int,
                extract(day from date)::int,
                extract(isodow from date)::int
            from silver_prices
            on conflict (date_key) do nothing;
        """)
        
        print("loading: fact_card_metrics")
        cur.execute("""
            insert into fact_card_metrics (card_key, set_key, max_attack_damage)
            select 
                dc.card_key,
                ds.set_key,
                max(nullif(regexp_replace(a.damage, '[^0-9]', '', 'g'), '')::integer)
            from silver_cards sc
            join dim_cards dc on sc.card_id = dc.card_id
            left join dim_sets ds on sc.set_id = ds.set_id
            left join silver_attacks a on sc.card_id = a.card_id
            group by dc.card_key, ds.set_key;
        """)
        
        print("loading: fact_prices")
        cur.execute("""
            insert into fact_prices (date_key, card_key, set_key, market_price_usd)
            select 
                to_char(sp.date, 'YYYYMMDD')::integer,
                dc.card_key,
                ds.set_key,
                sp.market_price_usd
            from silver_prices sp
            join dim_cards dc on sp.card_id = dc.card_id
            join dim_sets ds on sp.set_id = ds.set_id;
        """)
        
        conn.commit()
        end_time = time.time()
        
        print(f"done: gold layer in {round(end_time - start_time, 2)}s")

    except Exception as e:
        print(f"error: {e}")
        conn.rollback()
    finally:
        if 'cur' in locals() and cur:
            cur.close()
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    load_gold_layer()