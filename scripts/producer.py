from multiprocessing import Queue
import threading
from typing import Callable

class Producer:
    def __init__(self, queue: Queue):
        self.queue = queue
        self.thread = None
        self.running = False

    def run(self, process: Callable):
        self.running = True

        def target():
            process(self.queue)

        self.thread = threading.Thread(target=target)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
