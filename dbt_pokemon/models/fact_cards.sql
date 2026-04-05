{{ config(materialized='table') }}

WITH silver_cards AS (
    SELECT * FROM {{ source('raw_pokemon', 'silver_cards') }}
),
-- references
dim_sets AS (
    SELECT * FROM {{ ref('dim_sets') }}
),
dim_rarity AS (
    SELECT * FROM {{ ref('dim_rarity') }}
),
dim_artists AS (
    SELECT * FROM {{ ref('dim_artists') }}
),

attack_stats AS (
    SELECT 
        card_id,
        MAX(damage::INTEGER) AS max_attack_damage,
        ROUND(AVG(damage::DECIMAL), 2) AS avg_attack_damage
    FROM {{ source('raw_pokemon', 'silver_attacks') }}
    GROUP BY card_id
),
cost_stats AS (
    SELECT 
        card_id,
        SUM(cost_value::INTEGER) AS energy_cost_total
    FROM {{ source('raw_pokemon', 'silver_attack_costs') }}
    GROUP BY card_id
)

SELECT
    ROW_NUMBER() OVER (ORDER BY c.card_id) AS fact_key,
    c.card_id,
    s.set_key,
    r.rarity_key,
    a.artist_key,
    c.hp AS hp_value,
    atk.max_attack_damage,
    atk.avg_attack_damage,
    cst.energy_cost_total,
    -- Sprawdzanie, czy to ewolucja (zakładam, że w subtypes jest słowo 'Stage')
    CASE WHEN c.subtypes ILIKE '%stage%' THEN TRUE ELSE FALSE END AS is_evolution,
    c.market_price,
    CURRENT_TIMESTAMP AS inserted_at
FROM silver_cards c
LEFT JOIN dim_sets s ON c.set_id = s.set_id
LEFT JOIN dim_rarity r ON c.rarity = r.rarity_name
LEFT JOIN dim_artists a ON c.artist = a.artist_name  -- dostosuj złączenie, jeśli linkujesz artystów inaczej
LEFT JOIN attack_stats atk ON c.card_id = atk.card_id
LEFT JOIN cost_stats cst ON c.card_id = cst.card_id