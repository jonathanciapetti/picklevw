"""
This module handles the multiprocessing tasks for loading and processing pickle files.
"""

from multiprocessing import Queue, Process
from tkinter import filedialog as fd
from pickle import UnpicklingError
import gzip
import psutil
from prettyprinter import pformat
from pandas import read_pickle

pids_queue = Queue()
output_queue = Queue()


def process_data(filename: str) -> None:
    """Processes the given file, reads its contents, and updates the output queue.

    :param filename: The name of the file to process.
    """
    while not output_queue.empty():
        output_queue.get()

    message = {
        "status": "start",
        "filename": "",
        "output": "",
    }
    output_queue.put(message)

    if not filename:
        return

    try:
        message["status"] = "loading"
        output_queue.put(message)
        with open(filename, "rb") as file:
            if file.read(2) == b"\x1f\x8b":  # Gzip check
                file = gzip.open(filename, "rb")
            message["filename"] = filename
            message["output"] = pformat(read_pickle(file), indent=4, compact=False)
    except FileNotFoundError as file_not_found_err:
        message["messagebox"] = f"File not found: {file_not_found_err}"
        message["status"] = "failed"
    except UnicodeDecodeError as unicode_decode_err:
        message["messagebox"] = f"Not a text pickle file: {unicode_decode_err}"
        message["status"] = "failed"
    except UnpicklingError as unpickling_err:
        message["messagebox"] = f"Not a valid pickle file: {unpickling_err}"
        message["status"] = "failed"
    except Exception as ex:
        message["messagebox"] = str(ex)
        message["status"] = "failed"
    else:
        message["status"] = "completed"

    output_queue.put(message)  # Final update to queue


def start_process() -> None:
    """Starts a separate process that runs the task function."""
    terminate_all_processes()
    filename = fd.askopenfilename()
    process = Process(target=process_data, args=(filename,))
    process.start()
    pids_queue.put(process.pid)


def terminate_all_processes() -> None:
    """Terminates all running processes recorded in the pids_queue."""
    while not pids_queue.empty():
        old_pid = pids_queue.get()
        try:
            proc = psutil.Process(old_pid)
            proc.terminate()  # or proc.kill() for extreme cases (it sends a SIGKILL)
        except psutil.NoSuchProcess:
            pass  # Process already terminated
