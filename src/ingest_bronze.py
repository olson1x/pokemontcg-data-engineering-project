import requests
import json

# import ścieżek z configu
from src.config import CARDS_DIR, ALL_SETS_FILE

# endpointy do mirrora danych
URL_SETS = "https://raw.githubusercontent.com/PokemonTCG/pokemon-tcg-data/master/sets/en.json"
BASE_CARDS_URL = "https://raw.githubusercontent.com/PokemonTCG/pokemon-tcg-data/master/cards/en"

def ingest_all():
    try:
        # storage structure check dla warstwy bronze
        CARDS_DIR.mkdir(parents=True, exist_ok=True)
        
        # ingest setów
        res_sets = requests.get(URL_SETS)
        res_sets.raise_for_status()
        sets_data = res_sets.json()
        
        # persistence warstwy bronze dla setów
        with open(ALL_SETS_FILE, "w", encoding="utf-8") as f:
            json.dump({"data": sets_data}, f, ensure_ascii=False, indent=4)
            
    except Exception as e:
        print(f"Sets uploaded unsuccesfully: {e}")
        return

    # ingest kart per set_id
    set_ids = [s['id'] for s in sets_data]
    for s_id in set_ids:
        
        path = CARDS_DIR / f"{s_id}.json"
        
        # unikamy redundancji danych
        if path.exists():
            continue

        try:
            # request do bronze layer dla kart danego setu
            response = requests.get(f"{BASE_CARDS_URL}/{s_id}.json")
            
            if response.status_code == 200:
                with open(path, "w", encoding="utf-8") as f:
                    # zapisujemy sformatowany JSON z poprawnym kodowaniem Pokémon
                    json.dump({"data": response.json()}, f, ensure_ascii=False, indent=4)
                
                # monitoring postępu
                print(f"Ingested: {s_id}")
            else:
                print(f"HTTP Error {response.status_code} for setid: {s_id}")
                
        except Exception as e:
            print(f"Error for setid: {s_id}: {e}")

if __name__ == "__main__":
    ingest_all()