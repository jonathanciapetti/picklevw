import gzip
import json

from pandas import read_pickle

def load_pickle(file):
    file_start = file.read(2)
    file.seek(0)
    with gzip.open(file, "rb") if file_start == b"\x1f\x8b" else file as f:
        return read_pickle(f)

def is_json_serializable(obj):
    try:
        json.dumps(obj)
        return True
    except (TypeError, OverflowError):
        return False
