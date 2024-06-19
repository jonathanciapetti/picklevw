"""
ABC

"""
import multiprocessing
from multiprocessing import Process
import gzip
import pickle

import psutil
from prettyprinter import pformat
from pandas import read_pickle

from src.imports import fd

pids_queue = multiprocessing.Queue()
output_queue = multiprocessing.Queue()
queue_input = {
    'status': 'start',
    'filename': '',
    'output': '',
}
output_queue.put(queue_input)


def process_data(filename):
    """

    :param filename:
    :return:
    """
    output_queue.empty()
    message = queue_input
    if not filename:
        return
    try:
        while not output_queue.empty():
            message = output_queue.get_nowait()
        message['status'] = 'loading'
        output_queue.put(message)
        with open(filename, "rb") as file:
            # https://stackoverflow.com/questions/3703276/how-to-tell-if-a-file-is-gzip-compressed
            # https://stackoverflow.com/questions/56125182/unpicklingerror-invalid-load-key-x1f
            if file.read(2) == b'\x1f\x8b':
                file = gzip.open(filename, 'rb')
            message['filename'] = filename
            message['output'] = pformat(read_pickle(file), indent=4, compact=False)

    except FileNotFoundError as err:
        print(f"(FileNotFoundError) {err}")
    except UnicodeDecodeError as err:
        # tk.messagebox.showerror(message="Not a text pickle file.")
        print(f"(UnicodeDecodeError) {err}")
    except pickle.UnpicklingError as err:
        # tk.messagebox.showerror(message=f"Not a valid pickle file: {err}")
        print(f"(pickle.UnpicklingError) {err}")
    # except Exception as ex:
    #     print(f"(Exception) {ex}")
    else:
        message['status'] = 'completed'
        output_queue.put(message)


def start_process():
    """Starts a separate process that runs the task function."""
    while not pids_queue.empty():
        old_pid = pids_queue.get_nowait()
        print(f'Terminating process with PID {old_pid}')
        proc = psutil.Process(old_pid)
        proc.terminate()  # or proc.kill()
    filename = fd.askopenfilename()
    process = Process(target=process_data, args=(filename,))
    process.start()
    pids_queue.put(process.pid)


def terminate_all_processes():
    """
    abc
    :return:
    """
    while not pids_queue.empty():
        old_pid = pids_queue.get_nowait()
        print(f'Terminating process with PID {old_pid}')
        proc = psutil.Process(old_pid)
        proc.terminate()
