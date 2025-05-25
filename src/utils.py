import io
import gzip
import json
import pickle
from typing import Any, Tuple, Optional, Union

import pandas as pd
from fickling.analysis import check_safety
from fickling.exception import UnsafeFileError
from fickling.fickle import Pickled
from streamlit.runtime.uploaded_file_manager import UploadedFile

import config as cfg
from exceptions import ExceptionUnsafePickle


class PickleSecurityChecker:
    SEVERITY_THRESHOLD = 1

    def __init__(self, buffer: io.BytesIO):
        self.buffer = buffer

    def ensure_safe(self):
        pf = Pickled.load(self.buffer)
        severity = check_safety(pf).severity
        if severity.value[0] > self.SEVERITY_THRESHOLD:
            raise UnsafeFileError(info="", filepath="")


class PickleReader:
    def __init__(self, buffer: io.BytesIO):
        self.buffer = buffer

    def try_read_dataframe(self) -> Optional[pd.DataFrame]:
        try:
            self.buffer.seek(0)
            obj = pd.read_pickle(self.buffer)
            return obj if isinstance(obj, (pd.DataFrame, pd.Series)) else None
        except (pickle.UnpicklingError, EOFError, ValueError):
            return None

    def try_read_objects(self) -> Tuple[Union[str, Any, None], bool]:
        self.buffer.seek(0)
        objects = []
        try:
            while True:
                objects.append(pickle.load(self.buffer))
        except (EOFError, pickle.UnpicklingError):
            pass
        except Exception as e:
            pass

        if len(objects) > 1:
            return ", ".join(map(str, objects)), True
        elif len(objects) == 1:
            return objects[0], False
        return None, False


class PickleLoader:
    def __init__(self, file: UploadedFile, allow_unsafe_file: bool = False):
        self.file = file
        self.allow_unsafe_file = allow_unsafe_file
        self.raw_data = self._read_file()
        self.is_gzipped = self.raw_data.startswith(b"\x1f\x8b")
        self.buffer = self._get_buffer()

    def _read_file(self) -> bytes:
        self.file.seek(0)
        return self.file.read()

    def _get_buffer(self) -> io.BytesIO:
        data = gzip.decompress(self.raw_data) if self.is_gzipped else self.raw_data
        return io.BytesIO(data)

    def load(self) -> Tuple[Any, bool, bool]:
        try:
            # Always check safety first
            safety_buffer = io.BytesIO(self.buffer.getvalue())
            PickleSecurityChecker(safety_buffer).ensure_safe()
            # Proceed to safe deserialization
            reader = PickleReader(io.BytesIO(self.buffer.getvalue()))
            df = reader.try_read_dataframe()
            if df is not None:
                return df, False, True

            obj, multiple = reader.try_read_objects()
            return obj, multiple, False

        except UnsafeFileError:
            if self.allow_unsafe_file:
                # Try to read anyway, but only if it is a DataFrame
                reader = PickleReader(io.BytesIO(self.buffer.getvalue()))
                df = reader.try_read_dataframe()
                if df is not None:
                    return df, False, True

            raise ExceptionUnsafePickle(cfg.MESSAGES["POTENTIAL_THREAT"])


def is_json_serializable(obj: Any) -> bool:
    try:
        json.dumps(obj)
        return True
    except (TypeError, OverflowError):
        return False
