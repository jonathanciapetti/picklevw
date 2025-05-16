import io
import gzip
import json
import pickle
from typing import Any, Tuple

import pandas as pd
from fickling.analysis import check_safety
from fickling.exception import UnsafeFileError
from fickling.fickle import Pickled
from streamlit.runtime.uploaded_file_manager import UploadedFile

from exceptions import ExceptionUnsafePickle


class PickleSecurityChecker:
    def __init__(self, data: bytes, is_gzipped: bool):
        self.data = data
        self.is_gzipped = is_gzipped

    def _get_buffer(self) -> io.BytesIO:
        return io.BytesIO(gzip.decompress(self.data) if self.is_gzipped else self.data)

    def ensure_safe(self):
        pf = Pickled.load(self._get_buffer())
        severity = check_safety(pf).severity
        if severity.value[0] > 2:  #  not in (Severity.LIKELY_SAFE, Severity.SUSPICIOUS, Severity.LIKELY_UNSAFE):
            raise UnsafeFileError(info='', filepath='')


class PickleReader:
    def __init__(self, data: bytes, is_gzipped: bool):
        self.data = data
        self.is_gzipped = is_gzipped

    def _get_buffer(self) -> io.BytesIO:
        return io.BytesIO(gzip.decompress(self.data) if self.is_gzipped else self.data)

    def try_read_dataframe(self) -> pd.DataFrame | None:
        try:
            df = pd.read_pickle(self._get_buffer())
            if isinstance(df, pd.DataFrame):
                return df
        except Exception:
            return None

    def try_read_objects(self) -> Tuple[Any, bool]:
        res = []
        buffer = self._get_buffer()
        try:
            while True:
                res.append(pickle.load(buffer))
        except Exception:
            pass
        if len(res) > 1:
            return ', '.join(map(str, res)), True
        elif len(res) == 1:
            return res[0], False
        return None, False


class PickleLoader:
    def __init__(self, file: UploadedFile):
        self.file = file
        self.raw_data = self._read_file()
        self.is_gzipped = self.raw_data[:2] == b"\x1f\x8b"

    def _read_file(self) -> bytes:
        self.file.seek(0)
        return self.file.read()

    def load(self) -> Tuple[Any, bool, bool]:
        try:
            # Step 1: Validate safety
            PickleSecurityChecker(self.raw_data, self.is_gzipped).ensure_safe()

            # Step 2: Try pandas
            reader = PickleReader(self.raw_data, self.is_gzipped)
            df = reader.try_read_dataframe()
            if df is not None:
                return df, False, True

            # Step 3: Try generic pickle
            obj, were_spared = reader.try_read_objects()
            return obj, were_spared, False

        except UnsafeFileError:
            raise ExceptionUnsafePickle("A potential **threat** has been detected in this file. Stopped loading.")
        except Exception as ex:
            raise ex

def is_json_serializable(obj: Any) -> bool:
    try:
        json.dumps(obj)
        return True
    except (TypeError, OverflowError):
        return False
