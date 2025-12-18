from multiprocessing import Process
from .producer import Producer
from .consumer import run_consumer
from .ipc_queue import create_ipc_queue
from config import DVF, dvf_clean
import pandas as pd

from typing import Optional, Tuple
import httpx

n_thread = 5

def load_df(data_path):
    return pd.read_csv(data_path, sep='|', decimal=",", compression="zip", low_memory=False)

# Producer function
def generate_data(queue):
    global n_thread
    
    df = load_df(DVF)
    # Sélection des colonnes pour calculer [Surface habitable]
    df_new = df[['Date mutation', 'Nature mutation', 'Valeur fonciere', 'Code postal', 'Code departement', 'Code commune', 'Surface Carrez du 1er lot', 'Surface Carrez du 2eme lot', 'Surface Carrez du 3eme lot', 'Surface Carrez du 4eme lot', 'Surface Carrez du 5eme lot', 'Nombre pieces principales', 'Surface reelle bati', 'Surface terrain', 'Type de voie', 'Type local', 'Commune']]
    # Suppression des doublons
    df_new = df_new.drop_duplicates()
    # Remplacement des NaN par 0.00 dans les colonnes avec des valeurs numerique pour le calcul de [Surface habitable]
    df_new = df_new.fillna(.0)
    #creation commune postale
    df_new['commune_postal'] = df_new['Commune'].astype(str) + ', ' + df_new['Code postal'].astype(str)
    for i, row in df_new.iterrows():
        code_postal = row['commune_postal']
        queue.put(code_postal)
        #time.sleep(0.2)
    # Poison pills pour les threads du ThreadPool (2 threads)
    for _ in range(n_thread):
        queue.put(None)


async def validate_and_geocode_address(address: str) -> Tuple[bool, Optional[dict]]:
    if not address or len(address) < 5:
        return False, None

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                "https://api-adresse.data.gouv.fr/search/",
                params={"q": address, "limit": 1},
            )
            response.raise_for_status()

        data = response.json()

        if not data.get("features"):
            return False, None

        feature = data["features"][0]
        geocode_data = {
            "latitude": feature["geometry"]["coordinates"][1],
            "longitude": feature["geometry"]["coordinates"][0],
            "citycode": feature["properties"].get("citycode"),
            "score": feature["properties"].get("score", 0),
        }

        return geocode_data["score"] >= 0.5, geocode_data

    except httpx.HTTPError:
        return False, None
    except Exception:
        return False, None


# Worker processing function
def process_data(item, pid):
    """
    Fonction exécutée par chaque thread du ThreadPool.
    Elle reçoit une adresse (item) depuis la Queue et lance la
    vérification / géocodage, puis écrit un résultat dans un fichier.
    """
    import asyncio

    try:
        is_valid, geocode_data = asyncio.run(validate_and_geocode_address(item))
    except Exception as e:
        is_valid, geocode_data = False, None
        error = str(e)
    else:
        error = ""

    with open(f"output{pid}.txt", "a", encoding="utf-8") as f:
        if is_valid and geocode_data:
            f.write(
                f"[worker {pid}] OK   | {item} "
                f"| lat={geocode_data['latitude']}, lon={geocode_data['longitude']}, "
                f"citycode={geocode_data['citycode']}, score={geocode_data['score']}\n"
            )
        else:
            f.write(
                f"[worker {pid}] FAIL | {item} "
                f"| geocoding invalide ou erreur: {error}\n"
            )


# Producer process
def process_producer(queue):
    producer = Producer(queue)
    producer.run(generate_data)
    producer.stop()


# Main launcher
def main():
    ipc_queue = create_ipc_queue()
    pp = Process(target=process_producer, args=(ipc_queue,))
    pc = Process(target=run_consumer, args=(ipc_queue,))

    try:
        pp.start()
        pc.start()
    except KeyboardInterrupt:
        print("Ctrl+C reçu : arrêt des processus...")
        pp.terminate()
        pc.terminate()
    
    pp.join()
    pc.join()


if __name__ == "__main__":
    main()
