-- tworzenie warstwy gold


CREATE TABLE dim_sets (
    set_key SERIAL PRIMARY KEY,
    set_id VARCHAR(50),
    set_name VARCHAR(255),
    series VARCHAR(100),
    release_year INTEGER
);

CREATE TABLE dim_rarity (
    rarity_key SERIAL PRIMARY KEY,
    rarity_name VARCHAR(50)
);


-- fact table (for analytic purposes)

CREATE TABLE fact_cards (
    fact_key SERIAL PRIMARY KEY,
    card_id VARCHAR(50),
    set_key INTEGER REFERENCES dim_sets(set_key),
    rarity_key INTEGER REFERENCES dim_rarity(rarity_key),
    hp_value INTEGER,
    is_holo BOOLEAN
);