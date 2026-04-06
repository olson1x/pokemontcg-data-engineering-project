-- DIM TABLES

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

CREATE TABLE dim_types (
    type_key SERIAL PRIMARY KEY,
    type_name VARCHAR(50) UNIQUE NOT NULL
);


-- FACT TABLE


CREATE TABLE fact_cards (
    fact_key SERIAL PRIMARY KEY,
    
    -- Degenerate Dimensions
    card_id VARCHAR(50) UNIQUE,
    card_name VARCHAR(255),
    supertype VARCHAR(50),
    evolves_from VARCHAR(255),
    evolves_to VARCHAR(255),
    
    -- Foreign keys
    set_key INTEGER REFERENCES dim_sets(set_key),
    rarity_key INTEGER REFERENCES dim_rarity(rarity_key),
    artist_key INTEGER REFERENCES dim_artists(artist_key),
    primary_type_key INTEGER REFERENCES dim_types(type_key),
    weakness_type_key INTEGER REFERENCES dim_types(type_key),
    resistance_type_key INTEGER REFERENCES dim_types(type_key),
    -- Values
    weakness_value VARCHAR(10),
    resistance_value VARCHAR(10),
    hp_value INTEGER,
    max_attack_damage INTEGER,
    avg_attack_damage DECIMAL(10,2),
    energy_cost_total INTEGER,
    market_price DECIMAL(10,2),
    
    inserted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);