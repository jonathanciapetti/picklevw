"""
Module for securely loading pickle files and checking JSON serializability.
"""

import gzip
import io
import json
import pickle
from typing import Any, Tuple

import pandas
from fickling import always_check_safety, is_likely_safe
from fickling.analysis import check_safety, Severity
from fickling.exception import UnsafeFileError
from fickling.fickle import Pickled
from pandas import read_pickle
from streamlit.runtime.uploaded_file_manager import UploadedFile

from exceptions import ExceptionUnsafePickle


# always_check_safety()


def load_pickle(file: UploadedFile | list[UploadedFile] | None) -> Tuple[Any, bool, bool]:
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
    file.seek(0)
    raw_data = file.read()
    file.seek(0)
    is_gzipped = raw_data[:2] == b"\x1f\x8b"
    try:
        buffer_for_analysis = io.BytesIO(gzip.decompress(raw_data) if is_gzipped else raw_data)
        pf = Pickled.load(buffer_for_analysis)
        severity_ = check_safety(pf).severity
        if severity_ not in (Severity.LIKELY_SAFE, Severity.LIKELY_UNSAFE):
            raise UnsafeFileError(info='', filepath='')

        buffer_for_pickle = io.BytesIO(gzip.decompress(raw_data) if is_gzipped else raw_data)
        with buffer_for_pickle as bf:
            try:
                if isinstance(df := pandas.read_pickle(bf), pandas.DataFrame):
                    return df, False, True
            except Exception:
                pass

        buffer_for_pickle = io.BytesIO(gzip.decompress(raw_data) if is_gzipped else raw_data)
        with buffer_for_pickle as bf:
            res = []
            try:
                while True:
                    obj = pickle.load(bf)
                    res.append(obj)
            except Exception:
                pass
            if len(res) > 1:
                return ', '.join(map(str, res)), True, False
            if len(res) == 1:
                return res[0], False, False
            return None, False, False
    except UnsafeFileError:
        raise ExceptionUnsafePickle(f"Potential **threat** detected in this file. Stopped loading.")
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
