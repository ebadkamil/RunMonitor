"""
Run Visualization software

Author: Ebad Kamil <ebad.kamil@xfel.eu>
All rights reserved.
"""
from datetime import datetime
import multiprocessing as mp
import queue
import time

from .proposal_monitor import ProposalMonitor


class RunServer(mp.Process):
    def __init__(self, proposal, data_queue):
        super().__init__()
        self.data_queue = data_queue

        self.proposal_monitor = ProposalMonitor(proposal)

    def run(self):
        while True:
            self.proposal_monitor.monitor()

            if not self.proposal_monitor.info:
                continue

            timestamp = datetime.now().strftime("%H:%M:%S")
            self.proposal_monitor.timestamp = timestamp

            try:
                self.data_queue.put_nowait(self.proposal_monitor)
                time.sleep(10)
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
