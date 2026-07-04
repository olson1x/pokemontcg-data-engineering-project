# pokemon tcg - etl vs elt architecture comparison

this project provides a practical comparison between the two most popular data engineering paradigms: etl (extract, transform, load) and elt (extract, load, transform). we use pokemon trading card data and synthetic market prices to demonstrate differences in performance, scalability, and flexibility.

---

## project goal

the main objective is to integrate technical and market data using two distinct processing paths and compare their outcomes.

## data sources

* json (pokemon tcg data)
* csv (synthetic market prices)

### etl path (python-driven)
* **process:** all transformation logic (cleaning, data typing, relational mapping) is executed in python before loading the data into the database.
* **use case:** precise object-oriented control and handling complex logic in code.
* **flow:** python scripts process raw local files and insert cleaned data directly into structured silver and gold tables.

### elt path (dbt-driven)
* **process:** fast ingestion of raw data directly into postgresql staging tables using native database commands (e.g., `copy`), bypassing python transformations entirely. once loaded, all data modeling is handled via pure sql using dbt.
* **use case:** leveraging the database engine's compute power, optimized for modern data warehouse environments.
* **flow:** raw files -> postgres staging (jsonb/raw text) -> dbt models -> silver/gold tables.

---

## tech stack

* **language:** python 3.x (etl engine)
* **database:** postgresql (elt engine & storage)
* **transformations:** dbt (data build tool)
* **ops:** docker & docker compose
* **libraries:** `psycopg2`, `python-dotenv`

---

## data architecture (medallion)

* **bronze (raw):** raw input files stored locally (json/csv).
* **staging (elt only):** technical tables in the database storing data exactly "as-is" (e.g., raw json strings).
* **silver:** normalized relational model (cards, sets, bridge tables).
* **gold:** star schema (fact and dimension tables) optimized for bi and analytics.