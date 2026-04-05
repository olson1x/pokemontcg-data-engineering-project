{{ config(materialized='table') }}

WITH source_data AS (
    SELECT DISTINCT rarity AS rarity_name
    FROM {{ source('raw_pokemon', 'silver_cards') }}
    WHERE rarity IS NOT NULL
)

SELECT
    ROW_NUMBER() OVER (ORDER BY rarity_name) AS rarity_key,
    rarity_name
FROM source_data