"""
Module for securely loading pickle files and checking JSON serializability.
"""

import gzip
import json
import pickle
from typing import Any, Tuple, Iterable

from fickling import always_check_safety
from fickling.exception import UnsafeFileError
from streamlit.runtime.uploaded_file_manager import UploadedFile

from exceptions import ExceptionUnsafePickle

always_check_safety()


def load_pickle(file: UploadedFile | list[UploadedFile] | None) -> Tuple[Any, bool]:
    """
    Securely loads a pickle file, detecting and handling gzip compression, and checking for unsafe content.

    This function uses the `fickling` library to validate the safety of the pickle content.
    If the file appears to be gzipped (based on magic bytes), it will be decompressed before loading.

    Parameters
    ----------
    file : UploadedFile or list[UploadedFile] or None
        A single uploaded file or list of files as provided by Streamlit's file uploader.

    Returns
    -------
    Any
        The deserialized Python object.

    Raises
    ------
    ExceptionUnsafePickle
        If the file is identified as unsafe for unpickling.
    Exception
        For other exceptions during the loading process.
    """
    file_start = file.read(2)
    file.seek(0)
    try:
        file_stream = gzip.GzipFile(fileobj=file,  mode='rb') if file_start == b"\x1f\x8b" else file
        res = []
        try:
            while True:
                obj = pickle.load(file_stream)
                res.append(obj)
        except UnsafeFileError as err:
            raise ExceptionUnsafePickle(f"Potential **threat** detected in this file. Stopped loading.\n\nFickling analysis: {err.info}")
        except Exception:
            pass
        if len(res) > 1:
            return ', '.join(map(str, res)), True
        return res[0], False
    except Exception as ex:
        raise ex

def is_json_serializable(obj: Any) -> bool:
    """
    Checks if a given object can be serialized to a JSON string.

    Parameters
    ----------
    obj : Any
        The object to test for JSON serializability.

    Returns
    -------
    bool
        True if the object is serializable to JSON, False otherwise.
    """
    try:
        json.dumps(obj)
        return True
    except (TypeError, OverflowError):
        return False
