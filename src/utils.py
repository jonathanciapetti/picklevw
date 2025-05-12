import gzip
import json

from pandas import read_pickle
from fickling import always_check_safety
from fickling.exception import UnsafeFileError

always_check_safety()


def load_pickle(file):
    file_start = file.read(2)
    file.seek(0)
    with gzip.open(file, "rb") if file_start == b"\x1f\x8b" else file as f:
        try:
            return read_pickle(f)
        except UnsafeFileError:
            raise ExceptionUnsafePickle("Potential threat detected in this file. Stopped loading.")
        except Exception as ex:
            raise ex


def is_json_serializable(obj):
    try:
        json.dumps(obj)
        return True
    except (TypeError, OverflowError):
        return False


class ExceptionUnsafePickle(Exception):
    pass