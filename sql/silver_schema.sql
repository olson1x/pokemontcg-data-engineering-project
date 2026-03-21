-- tworzenie warstwy silver



CREATE TABLE silver_artists (
    artist_id SERIAL PRIMARY KEY,
    artist_name VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);





CREATE TABLE silver_sets (
    set_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    series VARCHAR(100),
    printed_total INTEGER,
    total INTEGER,
    release_date DATE,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);





CREATE TABLE silver_cards (
    card_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    supertype VARCHAR(50),
    hp INTEGER CHECK (hp >= 0),
    rarity VARCHAR(50) DEFAULT 'Unknown',
    evolves_from VARCHAR(255),
    flavor_text TEXT,
    image_url_small TEXT,
    image_url_large TEXT,
    artist_id INTEGER REFERENCES silver_artists(artist_id),
    set_id VARCHAR(50) REFERENCES silver_sets(set_id),
    market_price NUMERIC (10, 2)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);





CREATE TABLE silver_types (
    type_id SERIAL PRIMARY KEY,
    type_name VARCHAR(50) UNIQUE NOT NULL
);




CREATE TABLE silver_attacks (
    attack_id SERIAL PRIMARY KEY,
    card_id VARCHAR(50) REFERENCES silver_cards(card_id),
    name VARCHAR(255) NOT NULL,
    damage VARCHAR(50),
    description TEXT,
    converted_energy_cost INTEGER
);




CREATE TABLE silver_attack_costs (
    attack_id INTEGER REFERENCES silver_attacks(attack_id),
    type_id INTEGER REFERENCES silver_types(type_id),
    count INTEGER DEFAULT 1,
    PRIMARY KEY (attack_id, type_id)
);





CREATE TABLE silver_card_weaknesses (
    card_id VARCHAR(50) REFERENCES silver_cards(card_id),
    type_id INTEGER REFERENCES silver_types(type_id),
    value VARCHAR(10),
    PRIMARY KEY (card_id, type_id)
);


-- bridge table dla relacji many-to-many



CREATE TABLE silver_card_types (
    card_id VARCHAR(50) REFERENCES silver_cards(card_id),
    type_id INTEGER REFERENCES silver_types(type_id),
    PRIMARY KEY (card_id, type_id)
);