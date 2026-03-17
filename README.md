# Pokemon TCG Data Engineering Project

Projekt typu End-to-End demonstrujący dwa podejścia do procesowania danych: **ETL** oraz **ELT**.

## 🏗️ Project Structure

- `data/` - Surowe dane JSON pobrane z API (Bronze Layer).
- `sql/` - Definicje schematów bazodanowych dla warstw Silver i Gold.
- `src/`
    - `etl/` - Podejście **Extract-Transform-Load**: Python odpowiada za czyszczenie danych i logikę relacji przed zapisem do bazy.
    - `elt/` - Podejście **Extract-Load-Transform**: Surowy JSON trafia do bazy (Staging), a transformacja odbywa się za pomocą SQL.

## 🛠️ Technologies
- **Python**: Inżynieria danych i orkiestracja.
- **PostgreSQL**: Hurtownia danych (Medallion Architecture).
- **Docker**: (Soon) Konteneryzacja całego środowiska.

## 📈 Roadmap
1. [x] Budowa rurociągu ETL w Pythonie.
2. [ ] Budowa rurociągu ELT (JSONB + SQL Transformations).
3. [ ] Stworzenie warstwy Gold (Analitycznej).
4. [ ] Konteneryzacja (Docker).