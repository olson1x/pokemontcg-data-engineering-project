# Pokemon TCG Data Pipeline
Projekt Data Engineering, który pobiera dane z Pokemon TCG API, przechowuje je w lokalnej bazie PostgreSQL i procesuje przez warstwy Bronze, Silver oraz Gold.

## Architektura Medallion
Projekt realizuje architekturę Medallion:
- **Bronze**: Surowe pliki JSON pobrane z API.
- **Silver**: Relacyjna baza danych (PostgreSQL) ze znormalizowanymi tabelami (Karty, Ataki, Artyści).
- **Gold**: Tabele analityczne (Model Gwiazdy) zoptymalizowane pod raportowanie.

### Wymagania systemowe (Linux)
Przed uruchomieniem należy zainstalować pakiety systemowe:
```bash
sudo apt update
sudo apt install python3-venv libpq-dev python3-dev postgresql postgresql-contrib