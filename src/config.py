from pathlib import Path

# paths setup
BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
BRONZE_DIR = DATA_DIR / "bronze"
CARDS_DIR = BRONZE_DIR / "cards"
PRICES_DIR = BRONZE_DIR / "prices"

ALL_SETS_FILE = BRONZE_DIR / "all_sets.json"
MARKET_PRICES_FILE = PRICES_DIR / "market_prices.csv"