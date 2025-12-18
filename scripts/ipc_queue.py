from multiprocessing import Queue


def create_ipc_queue() -> Queue:
    """
    Crée et retourne une Queue de multiprocessing utilisée pour la
    communication entre le processus Producer et le processus Consumer.
    """
    return Queue()

