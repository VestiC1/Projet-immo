import threading
from typing import Callable
from multiprocessing import Queue

class Worker(threading.Thread):
    def __init__(self, process: Callable, queue: Queue, worker_id: int):
        super().__init__()
        self.process = process
        self.queue = queue
        self.worker_id = worker_id

    def run(self):
        while True:
            item = self.queue.get()
            if item is None:
                break
            self.process(item, self.worker_id)


