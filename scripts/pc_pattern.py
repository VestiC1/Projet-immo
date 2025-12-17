from multiprocessing import Process, Queue
from .producer import Producer
from .threadpool import ThreadPool
import time
from config import DVF, dvf_clean
import pandas as pd

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


# Worker processing function
def process_data(item, pid):
    with open(f"output{pid}.txt", "a") as f:
        f.write(f"Produced: {item}\n")


# Producer process
def process_producer(queue):
    producer = Producer(queue)
    producer.run(generate_data)
    producer.stop()


# Consumer process
def process_consumer(queue):
    global n_thread
    pool = ThreadPool(n_thread, queue, process_data)
    #pool.shutdown()


# Main launcher
def main():
    ipc_queue = Queue()
    pp = Process(target=process_producer, args=(ipc_queue,))
    pc = Process(target=process_consumer, args=(ipc_queue,))

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
