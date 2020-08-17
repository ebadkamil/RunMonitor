"""
Run Visualization software

Author: Ebad Kamil <ebad.kamil@xfel.eu>
All rights reserved.
"""
from datetime import datetime
import multiprocessing as mp
import queue
import time

from ..helpers import get_all_runs_size


class RunInfo:
    def __init__(self, timestamp):
        self._timestamp = timestamp
        self.size_info = None

    @property
    def timestamp(self):
        return self._timestamp


class RunServer(mp.Process):
    def __init__(self, proposal, data_queue):
        super().__init__()
        self.proposal = proposal
        self.data_queue = data_queue

    def run(self):
        while True:
            names = get_all_runs_size(self.proposal)

            timestamp = datetime.now().strftime("%H:%M:%S")
            data = RunInfo(timestamp)
            data.size_info = names

            try:
                self.data_queue.put_nowait(data)
                time.sleep(60)
            except queue.Full:
                continue


if __name__ == "__main__":
    dq = mp.Queue(maxsize=1)
    rs = RunServer("/media/kamile/storage/dssc_data/raw/", dq)
    rs.daemon = True
    rs.start()
    while True:
        try:
            data = dq.get_nowait()
            print(data.timestamp)
            print(data.size_info)
        except queue.Empty:
            continue
    rs.join()