# Pokemon TCG - ETL vs ELT Architecture Comparison 🃏⚖️

Projekt ma na celu praktyczne porównanie dwóch najpopularniejszych paradygmatów inżynierii danych: **ETL** (Extract, Transform, Load) oraz **ELT** (Extract, Load, Transform). Wykorzystujemy ten sam zbiór danych (Karty Pokémon), aby zademonstrować różnice w wydajności, skalowalności i elastyczności obu podejść.

---

## 🎯 Project Goal

Głównym założeniem jest integracja danych technicznych i rynkowych przy użyciu dwóch różnych ścieżek procesowania:

### ⚙️ Ścieżka ETL (Python-centric)
* **Dane:** JSON (GitHub API) / CSV (Synthetic data)
* **Proces:** Cała logika transformacji (czyszczenie, typowanie danych, mapowanie relacji) odbywa się w Pythonie przed załadowaniem do bazy.
* **Zastosowanie:** Precyzyjne sterowanie obiektowe, skomplikowana logika biznesowa w kodzie.

### ⚡ Ścieżka ELT (Database-centric)
* **Dane:** Te same źródła (JSON/CSV).
* **Proces:** Szybki import surowych danych (Raw/Staging) do PostgreSQL za pomocą komend systemowych (`COPY`), a następnie transformacja przy użyciu czystego SQL.
* **Zastosowanie:** Wykorzystanie mocy obliczeniowej silnika bazy danych, szybkość przy dużych wolumenach (Big Data).

---

## 🛠️ Tech Stack

* **Language:** Python 3.x (ETL Engine)
* **Database:** PostgreSQL (ELT Engine & Storage)
* **Ops:** Docker & Docker Compose (Containerization 🏗️)
* **Libraries:** `psycopg2`, `requests`, `python-dotenv`

---

## 📂 Data Architecture (Medallion)

* **Bronze (Raw):** Surowe pliki wejściowe (JSON/CSV).
* **Staging (ELT only):** Tymczasowe tabele techniczne przechowujące dane "as-is".
* **Silver (Production):** Docelowy model relacyjny (`cards`, `sets`, `artists`) zasilany obiema metodami dla porównania wyników.
