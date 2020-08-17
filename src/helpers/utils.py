"""
Run Visualization software

Author: Ebad Kamil <ebad.kamil@xfel.eu>
All rights reserved.
"""
from glob import iglob
import os


def find_proposal(proposal, data='raw'):
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
        if '/' in propno:
            # Already passed a proposal directory
            return propno

        for d in iglob(os.path.join(DATA_ROOT_DIR, '*/*/{}'.format(propno))):
            return d

        raise Exception("Couldn't find proposal dir for {!r}".format(propno))

    if isinstance(proposal, int):
        proposal = 'p{:06d}'.format(proposal)
    elif ('/' not in proposal) and not proposal.startswith('p'):
        proposal = 'p' + proposal.rjust(6, '0')

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
        b /= factor**2
    elif unit == "GB":
        b /= factor**3
    elif unit == "TB":
        b /= factor**4
    elif unit == "PB":
        b /= factor**5

    return b


def get_run_size(directory):
    """Returns the `directory` size in bytes."""
    total = 0
    try:
        # print("[+] Getting the size of", directory)
        for entry in os.scandir(directory):
            if entry.is_file():
                # if it's a file, use stat() function
                total += entry.stat().st_size
            elif entry.is_dir():
                # if it's a directory, recursively call this function
                total += get_directory_size(entry.path)
    except NotADirectoryError:
        # if `directory` isn't a directory, get the file size then
        return os.path.getsize(directory)
    except PermissionError:
        # if for whatever reason we can't open the folder, return 0
        return 0
    return total


def get_all_runs_size(path):
    # iterate over all the directories inside this path
    try:
        all_runs = os.listdir(path)
    except Exception as ex:
        print(ex)

    names = {}
    for run in sorted(all_runs):
        run = os.path.join(path, run)
        # get the size of this directory (folder)
        run_size = get_run_size(run)
        if run_size == 0:
            continue
        names[os.path.basename(run)] = run_size

    return names


# if __name__ == "__main__":
#     proposal = find_proposal("/media/kamile/storage/dssc_data/")
#     print(proposal)