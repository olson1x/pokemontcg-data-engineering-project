{{ config(materialized='table') }}

WITH source_data AS (
    SELECT DISTINCT artist_name
    FROM {{ source('raw_pokemon', 'silver_artists') }}
    WHERE artist_name IS NOT NULL
)

SELECT
    ROW_NUMBER() OVER (ORDER BY artist_name) AS artist_key,
    artist_name
FROM source_data