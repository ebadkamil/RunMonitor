"""
Run Visualization software

Author: Ebad Kamil <ebad.kamil@xfel.eu>
All rights reserved.
"""
from datetime import datetime
from functools import lru_cache
import multiprocessing as mp
import os
from pathlib import Path
import queue
from threading import Thread
import time

from extra_data.validation import FileValidator, RunValidator, ValidationError
from extra_data import H5File

from ..helpers import run_in_thread


class RunInfo:
    def __init__(self, timestamp):
        self._timestamp = timestamp
        self.info = None

    @property
    def timestamp(self):
        return self._timestamp


class ProposalMonitor(mp.Process):
    def __init__(self, proposal, data_queue, validate=False):
        super().__init__()
        self.proposal = proposal
        self.data_queue = data_queue
        self.validate = validate
        self._info = None

        self.__queue = queue.Queue()

    def run(self):
        monitor = self.monitor()
        while True:
            try:
                next(monitor)
            except StopIteration:
                continue

            if not self._info:
                continue

            timestamp = datetime.now().strftime("%H:%M:%S")
            self.data = RunInfo(timestamp)
            self.data.info = self._info

            try:
                self.data_queue.put(self.data)
            except queue.Full:
                continue

    def monitor(self):
        # watch the proposal directory in a separate thread
        self.watch()

        names = {}

        while True:
            run, creation_date = self.__queue.get()
            run = os.path.join(self.proposal, run)
            info = self._get_run_info(run, creation_date)
            if info == 0:
                continue
            print("GET ", run, info)
            names[os.path.basename(run)] = info
            self._info = names
            yield

    @run_in_thread
    def watch(self):
        old_runs = []
        diff = lambda a, b: [x for x in a if x not in b]
        m_time = lambda path: max(
            [entry.stat().st_mtime
             for entry in os.scandir(path) if entry.is_file()])

        while True:
            new_runs = []
            for run in sorted(os.listdir(self.proposal)):
                run = os.path.join(self.proposal, run)
                try:
                    timestamp = datetime.fromtimestamp(m_time(run))
                except Exception:
                    timestamp = datetime.fromtimestamp(
                        Path(run).stat().st_mtime)
                new_runs.append((run, timestamp))

            chunk = diff(new_runs, old_runs)
            for run in sorted(chunk):
                self.__queue.put(run)
            time.sleep(20)
            old_runs = new_runs

    @lru_cache(maxsize=300)
    def _get_run_info(self, path, creation_date):
        """Returns the `path` size in bytes and isvalidate."""
        total = 0
        try:
            for entry in os.scandir(path):
                # Only evaluates size of files and not folders inside raw/proc
                if entry.is_file():
                    # if it's a file, use stat() function
                    total += entry.stat().st_size

        except NotADirectoryError:
            # if `path` isn't a directory, get the file size then
            total = os.path.getsize(path)
        except PermissionError:
            # if for whatever reason we can't open the folder, return 0
            return 0

        if not self.validate:
            return total, " "

        if os.path.isdir(path):
            validator = RunValidator(path)
        elif path.endswith('.h5'):
            validator = FileValidator(H5File(path).files[0])
        else:
            return 0

        try:
            validator.run_checks()
        except Exception as ex:
            pass
        return total, str(ValidationError(validator.problems))


if __name__ == "__main__":
    dq = mp.Queue(maxsize=1)
    rs = ProposalMonitor("/gpfs/exfel/exp/FXE/202002/p002573/raw", dq)
    rs.start()
    while True:
        try:
            data = dq.get_nowait()
            # print(data.timestamp)
            # print(data.info)
        except queue.Empty:
            continue
    rs.join()
