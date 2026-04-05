{{ config(materialized='table') }}

WITH source_data AS (
    SELECT DISTINCT
        set_id,
        name AS set_name,
        series,
        release_date::DATE AS release_date,
        printed_total AS total_cards_in_set
    FROM {{ source('raw_pokemon', 'silver_sets') }}
)

SELECT
    ROW_NUMBER() OVER (ORDER BY release_date, set_id) AS set_key,
    set_id,
    set_name,
    series,
    release_date,
    EXTRACT(YEAR FROM release_date)::INTEGER AS release_year,
    total_cards_in_set
FROM source_data