"""
Run Visualization software

Author: Ebad Kamil <ebad.kamil@xfel.eu>
All rights reserved.
"""
import os
from functools import wraps
from glob import iglob
from threading import Thread


def find_proposal(proposal, data="raw"):
    """From EXtra-data

    Access EuXFEL data on the Maxwell cluster by proposal and run number.
    Parameters
    ----------
    proposal: int
        A proposal number, such as 2012, '2012', 'p002012', or a path such as
        '/gpfs/exfel/exp/SPB/201701/p002012'.
    run: str, int
        A run number such as 243, '243' or 'r0243'.
    data: str
        'raw' or 'proc' (processed) to access data from one of those folders.
        The default is 'raw'.

    Return:
    -------
    proposal_path: str
    """
    DATA_ROOT_DIR = "/gpfs/exfel/exp"

    def find_dir(propno):
        """Find the proposal directory for a given proposal on Maxwell"""
        if "/" in propno:
            # Already passed a proposal directory
            return propno

        for d in iglob(os.path.join(DATA_ROOT_DIR, "*/*/{}".format(propno))):
            return d

        raise Exception("Couldn't find proposal dir for {!r}".format(propno))

    if isinstance(proposal, int):
        proposal = "p{:06d}".format(proposal)
    elif ("/" not in proposal) and not proposal.startswith("p"):
        proposal = "p" + proposal.rjust(6, "0")

    prop_dir = find_dir(proposal)

    return os.path.join(prop_dir, data)


def get_size_format(b, unit="B", factor=1024):
    """
    Scale bytes to its proper byte format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    if unit == "KB":
        b /= factor
    elif unit == "MB":
        b /= factor ** 2
    elif unit == "GB":
        b /= factor ** 3
    elif unit == "TB":
        b /= factor ** 4
    elif unit == "PB":
        b /= factor ** 5

    return b


def run_in_thread(original):
    @wraps(original)
    def wrapper(*args, **kwargs):
        t = Thread(target=original, args=args, kwargs=kwargs, daemon=True)
        t.start()
        return t

    return wrapper


if __name__ == "__main__":
    # proposal = find_proposal("/media/kamile/storage/dssc_data/")
    # print(proposal)
    proposal = 2573
    proposal = find_proposal(proposal, data="raw")
    print("Proposal :", proposal)
