-- tworzenie warstwy silver

CREATE TABLE silver_artists (
    artist_id SERIAL PRIMARY KEY,
    artist_name VARCHAR(255) UNIQUE NOT NULL
);


CREATE TABLE silver_sets (
    set_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    series VARCHAR(100),
    printed_total INTEGER,
    total INTEGER,
    release_date DATE
);


CREATE TABLE silver_cards (
    card_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    supertype VARCHAR(50), 
    hp INTEGER,
    rarity VARCHAR(50),
    artist_id INTEGER REFERENCES silver_artists(artist_id),
    set_id VARCHAR(50) REFERENCES silver_sets(set_id)
);


CREATE TABLE silver_types (
    type_id SERIAL PRIMARY KEY,
    type_name VARCHAR(50) UNIQUE NOT NULL
);


-- bridge table dla relacji many-to-many

CREATE TABLE silver_card_types (
    card_id VARCHAR(50) REFERENCES silver_cards(card_id),
    type_id INTEGER REFERENCES silver_types(type_id),
    PRIMARY KEY (card_id, type_id)
);