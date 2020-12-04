"""
Run Visualization software

Author: Ebad Kamil <ebad.kamil@xfel.eu>
All rights reserved.
"""
from datetime import datetime
from functools import lru_cache
import os
from pathlib import Path

from extra_data.validation import FileValidator, RunValidator, ValidationError
from extra_data import H5File


class ProposalMonitor:
    def __init__(self, proposal):
        self.proposal = proposal
        self._info = None
        self._timestamp = None

    def monitor(self):
        try:
            all_runs = os.listdir(self.proposal)
        except Exception as ex:
            print("ERROR:", ex)
            return

        names = {}
        for idx, run in enumerate(sorted(all_runs)):
            run = os.path.join(self.proposal, run)
            creation_date = datetime.fromtimestamp(Path(run).stat().st_mtime)
            # get the size of this directory (folder)
            info = self._get_run_info(run, creation_date)

            if info == 0:
                continue
            names[os.path.basename(run)] = info
            self._info = names
            yield

    @property
    def info(self):
        return self._info

    @property
    def timestamp(self):
        return self._timestamp

    @timestamp.setter
    def timestamp(self, value):
        self._timestamp = value

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

        if os.path.isdir(path):
            validator = RunValidator(path)
        elif path.endswith('.h5'):
            validator = FileValidator(H5File(path).files[0])
        else:
            return 0

        validator.run_checks()
        return total, str(ValidationError(validator.problems))
