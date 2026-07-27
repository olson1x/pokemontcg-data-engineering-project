import requests
import json

# import ścieżek z configu
from src.config import CARDS_DIR, ALL_SETS_FILE

# endpointy do mirrora danych
URL_SETS = "https://raw.githubusercontent.com/PokemonTCG/pokemon-tcg-data/master/sets/en.json"
BASE_CARDS_URL = "https://raw.githubusercontent.com/PokemonTCG/pokemon-tcg-data/master/cards/en"

def ingest_all():
    # storage structure check dla warstwy bronze (korzystamy z pathlib)
    CARDS_DIR.mkdir(parents=True, exist_ok=True)
    
    # ingest setów
    res_sets = requests.get(URL_SETS)
    sets_data = res_sets.json()
    
    # persistence warstwy bronze dla setów
    with open(ALL_SETS_FILE, "w", encoding="utf-8") as f:
        json.dump({"data": sets_data}, f, ensure_ascii=False, indent=4)

    # ingest kart per set_id
    set_ids = [s['id'] for s in sets_data]
    for s_id in set_ids:
        # dynamiczne budowanie ścieżki do pliku
        path = CARDS_DIR / f"{s_id}.json"
        
        # unikamy redundancji danych (używamy metody exists() z pathlib)
        if path.exists():
            continue

        # request do bronze layer dla kart danego setu
        response = requests.get(f"{BASE_CARDS_URL}/{s_id}.json")
        if response.status_code == 200:
            with open(path, "w", encoding="utf-8") as f:
                # zapisujemy sformatowany JSON z poprawnym kodowaniem Pokémon
                json.dump({"data": response.json()}, f, ensure_ascii=False, indent=4)
            
            # monitoring postępu
            print(f"Ingested: {s_id}")

if __name__ == "__main__":
    ingest_all()