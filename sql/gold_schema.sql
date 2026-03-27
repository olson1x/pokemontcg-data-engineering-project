-- tworzenie warstwy gold





CREATE TABLE dim_sets (
    set_key SERIAL PRIMARY KEY,
    set_id VARCHAR(50),
    set_name VARCHAR(255),
    series VARCHAR(100),
    release_date DATE,
    release_year INTEGER,
    total_cards_in_set INTEGER
);





CREATE TABLE dim_rarity (
    rarity_key SERIAL PRIMARY KEY,
    rarity_name VARCHAR(50)
);





CREATE TABLE dim_artists (
    artist_key SERIAL PRIMARY KEY,
    artist_name VARCHAR(255)
);





-- fact table



CREATE TABLE fact_cards (
    fact_key SERIAL PRIMARY KEY,
    card_id VARCHAR(50),
    set_key INTEGER REFERENCES dim_sets(set_key),
    rarity_key INTEGER REFERENCES dim_rarity(rarity_key),
    artist_key INTEGER REFERENCES dim_artists(artist_key),
    hp_value INTEGER,
    max_attack_damage INTEGER,
    avg_attack_damage DECIMAL(10,2),
    energy_cost_total INTEGER,
    is_evolution BOOLEAN,
    market_price DECIMAL(10,2),
    inserted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);