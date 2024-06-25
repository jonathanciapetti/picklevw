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
queue_input = {
    'status': 'start',
    'filename': '',
    'output': '',
}
output_queue.put(queue_input)


def read_queue(msg: dict, queue: Queue) -> dict:
    """ Reads the latest message from the queue if available.

    :param msg: The current message dictionary.
    :param queue: The queue to read from.
    :return: The updated message dictionary.
    """
    while not queue.empty():
        msg = queue.get_nowait()
    return msg


def process_data(filename: str) -> None:
    """ Processes the given file, reads its contents, and updates the output queue.

    :param filename: The name of the file to process.
    """
    output_queue.empty()
    message = queue_input
    if not filename:
        return
    try:
        message = read_queue(message, output_queue)
        message['status'] = 'loading'
        output_queue.put(message)
        with open(filename, "rb") as file:
            if file.read(2) == b'\x1f\x8b':  # Gzip check
                file = gzip.open(filename, 'rb')
            message['filename'] = filename
            message['output'] = pformat(read_pickle(file), indent=4, compact=False)
    except FileNotFoundError as file_not_found_err:
        message['messagebox'] = f"File not found: {file_not_found_err}"
        message['status'] = 'failed'
        output_queue.put(message)
    except UnicodeDecodeError as unicode_decode_err:
        message['messagebox'] = f"Not a text pickle file: {unicode_decode_err}"
        message['status'] = 'failed'
        output_queue.put(message)
    except UnpicklingError as unpickling_err:
        message['messagebox'] = f"Not a valid pickle file: {unpickling_err}"
        message['status'] = 'failed'
        output_queue.put(message)
    except Exception as ex:
        message['messagebox'] = str(ex)
        message['status'] = 'failed'
        output_queue.put(message)
    else:
        message['status'] = 'completed'
        output_queue.put(message)


def start_process() -> None:
    """Starts a separate process that runs the task function."""
    while not pids_queue.empty():
        terminate_all_processes()
    filename = fd.askopenfilename()
    process = Process(target=process_data, args=(filename,))
    process.start()
    pids_queue.put(process.pid)


def terminate_all_processes() -> None:
    """ Terminates all running processes recorded in the pids_queue. """
    while not pids_queue.empty():
        old_pid = pids_queue.get_nowait()
        # print(f'Terminating process with PID {old_pid}')
        proc = psutil.Process(old_pid)
        proc.terminate()  # or proc.kill() for extreme cases (it sends a SIGKILL)
