from .worker import Worker
from multiprocessing import Queue
from typing import Callable

class ThreadPool:
    def __init__(self, num_workers: int, queue: Queue, process: Callable):
        self.queue = queue
        self.workers = []

        for i in range(num_workers):
            print(i)
            worker = Worker(process, self.queue, i)
            worker.start()          # 🔥 PARALLÈLE
            self.workers.append(worker)

    def shutdown(self):
        # poison pill pour chaque worker
        for _ in self.workers:
            self.queue.put(None)

        for worker in self.workers:
            worker.join()