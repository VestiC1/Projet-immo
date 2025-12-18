from .threadpool import ThreadPool
from .pc_pattern import process_data, n_thread
from multiprocessing import Queue


def run_consumer(ipc_queue: Queue) -> None:
    """
    Démarre le ThreadPool côté Consumer pour traiter les éléments
    reçus dans la Queue IPC.

    Le Producer se charge déjà d'envoyer n_thread poison pills (None),
    donc les threads s'arrêteront naturellement lorsque la Queue sera
    épuisée.
    """
    ThreadPool(n_thread, ipc_queue, process_data)

