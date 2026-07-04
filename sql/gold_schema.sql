-- drop existing tables
drop table if exists fact_prices cascade;
drop table if exists fact_card_metrics cascade;
drop table if exists bridge_card_types cascade;
drop table if exists bridge_card_subtypes cascade;
drop table if exists dim_types cascade;
drop table if exists dim_subtypes cascade;
drop table if exists dim_cards cascade;
drop table if exists dim_sets cascade;
drop table if exists dim_date cascade;

-- dim tables
create table dim_sets (
    set_key serial primary key,
    set_id varchar(50) unique not null,
    set_name varchar(255),
    series varchar(100),
    release_date date,
    release_year integer,
    total_cards_in_set integer
);

create table dim_cards (
    card_key serial primary key,
    card_id varchar(50) unique not null,
    card_name varchar(255),
    supertype varchar(50),
    rarity varchar(50),
    hp_value integer,
    artist_name varchar(255),
    evolves_from varchar(255),
    evolves_to text
);

create table dim_date (
    date_key integer primary key,
    full_date date,
    year integer,
    month integer,
    day integer,
    day_of_week integer
);

create table dim_types (
    type_key serial primary key,
    type_name varchar(50) unique not null
);

create table dim_subtypes (
    subtype_key serial primary key,
    subtype_name varchar(255) unique not null
);

-- bridge tables
create table bridge_card_types (
    card_key integer references dim_cards(card_key),
    type_key integer references dim_types(type_key),
    primary key (card_key, type_key)
);

create table bridge_card_subtypes (
    card_key integer references dim_cards(card_key),
    subtype_key integer references dim_subtypes(subtype_key),
    primary key (card_key, subtype_key)
);

-- fact tables
create table fact_card_metrics (
    fact_key serial primary key,
    card_key integer references dim_cards(card_key),
    set_key integer references dim_sets(set_key),
    max_attack_damage integer,
    inserted_at timestamp default current_timestamp
);

create table fact_prices (
    price_key serial primary key,
    date_key integer references dim_date(date_key),
    card_key integer references dim_cards(card_key),
    set_key integer references dim_sets(set_key),
    market_price_usd numeric(10,2)
);