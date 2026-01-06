import io
import gzip
import json
import pickle
from typing import Any, Tuple, Optional, Union

import numpy as np
import pandas as pd
from fickling.analysis import check_safety
from fickling.exception import UnsafeFileError
from fickling.fickle import Pickled
from streamlit.runtime.uploaded_file_manager import UploadedFile

import config as cfg
from exceptions import ExceptionUnsafePickle


class PickleSecurityChecker:

    def __init__(self, buffer: io.BytesIO):
        self.buffer = buffer

    def ensure_safe(self):
        """
        Ensures that the loaded file is safe to process by checking its safety level against a
        predefined severity threshold.

        The function loads the data from a buffer using the `Pickled` module, analyzes its safety
        level using the `check_safety` function, and compares the resulting severity to the
        class-defined severity threshold. If the safety level exceeds the threshold, an
        `UnsafeFileError` is raised.

        :param self: The instance of the class that contains the buffer to check
            and the severity threshold.
        :type self: The class that owns this method
        :raises UnsafeFileError: If the severity level of the loaded file is
            beyond the acceptable threshold.
        :return: None
        """
        pf = Pickled.load(self.buffer)
        severity = check_safety(pf).severity
        if severity.value[0] > cfg.CONFIG["SEVERITY_THRESHOLD"]:
            raise UnsafeFileError(info="", filepath="")


class PickleReader:
    def __init__(self, buffer: io.BytesIO):
        self.buffer = buffer

    def try_read_dataframe(self) -> Optional[pd.DataFrame]:
        """
        Attempts to read a Pandas DataFrame or Series from a buffer using pickle.

        The function resets the position of the buffer to the beginning before reading. If the
        content is successfully unpickled, the function ensures it is either a DataFrame or Series
        instance before returning it.

        :returns: A Pandas DataFrame, Series, or None if the buffer cannot be read or does not
        contain valid data.
        :rtype: Optional[pd.DataFrame]
        """
        try:
            self.buffer.seek(0)
            obj = pd.read_pickle(self.buffer)
            return obj if isinstance(obj, (pd.DataFrame, pd.Series)) else None
        except (pickle.UnpicklingError, EOFError, ValueError):
            return None

    def try_read_array(self) -> Optional[Union[np.ndarray, pd.DataFrame, pd.Series, dict]]:
        """
        Attempts to read a supported object (NumPy ndarray, Pandas DataFrame/Series, or a dict containing image data)
        from a buffer using pickle.

        Resets the buffer position before reading. Supports:
        - np.ndarray: any shape, including images
        - pd.DataFrame or pd.Series
        - dicts with a 'data' key containing a valid ndarray (e.g. CIFAR-style)

        :returns: The unpickled object if it contains a supported structure; None otherwise.
        :rtype: Optional[Union[np.ndarray, pd.DataFrame, pd.Series, dict]]
        """
        try:
            self.buffer.seek(0)
            obj = pickle.load(self.buffer)

            if isinstance(obj, dict) and isinstance(obj.get("data"), np.ndarray):
                return obj  # e.g., CIFAR-style dict with image data

            if isinstance(obj, (pd.DataFrame, pd.Series, np.ndarray)):
                return obj

            return None
        except (pickle.UnpicklingError, EOFError, ValueError):
            return None

    def try_read_objects(self) -> Tuple[Union[str, Any, None], bool]:
        """
        Attempts to read serialized objects from the buffer using the pickle module.

        The method seeks the buffer to the beginning, then iteratively tries to load objects from
        the buffer until it encounters an EOFError or pickle.UnpicklingError.

        In case of any other unexpected exceptions, they are caught silently. After attempting to
        load objects, it determines the appropriate return values based on how many objects were
        successfully read.

        :return: A tuple containing two elements:
            - The first element is a string combining all extracted objects, a single
              object, or None if the buffer is empty or object deserialization fails.
            - The second element is a boolean indicating if multiple objects were read
              (True) or if a single or no object was read (False).
        :rtype: Tuple[Union[str, Any, None], bool]
        """
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
        """
        Reads the entire content of the associated file object starting from the beginning and
        returns it as a bytes object.

        :return: The content of the file as bytes.
        :rtype: bytes
        """
        self.file.seek(0)
        return self.file.read()

    def _get_buffer(self) -> io.BytesIO:
        """
        Decompresses the raw data if gzipped and returns it as a BytesIO object.

        :return: A BytesIO object containing the decompressed or raw data.
        :rtype: io.BytesIO
        """
        data = gzip.decompress(self.raw_data) if self.is_gzipped else self.raw_data
        return io.BytesIO(data)

    def load(self) -> Tuple[Any, bool, bool]:
        """
        Deserializes the provided buffer cautiously to ensure security, attempting to extract either
        a DataFrame or generic objects based on the serialized content. The function prioritizes
        safety by validating the pickle buffer before reading.

        If the buffer contains a valid DataFrame, it will return the DataFrame.
        If the buffer contains generic objects, it will attempt to read and return them.

        The function also handles cases where the buffer might be deemed unsafe, allowing unsafe
        reads for DataFrame if explicitly permitted.

        :return: A tuple containing the deserialized object (DataFrame or generic object), a boolean
            indicating whether multiple objects were deserialized, and a boolean flag indicating if
            the object returned is a DataFrame.
        :rtype: Tuple[Any, bool, bool]
        :raises UnsafeFileError: If the pickle buffer is determined to be unsafe and unsafe file
            reading is not allowed.
        :raises Exception: When deserialization is deemed unsafe and there are potential security
            threats due to unsafe pickle.
        """
        try:
            # Always check safety first
            safety_buffer = io.BytesIO(self.buffer.getvalue())
            PickleSecurityChecker(safety_buffer).ensure_safe()

            # Proceed to safe deserialization
            reader = PickleReader(io.BytesIO(self.buffer.getvalue()))
            obj, multiple = reader.try_read_objects()
            return obj, multiple, False

        except UnsafeFileError:
            if self.allow_unsafe_file:
                # Try to read anyway, but only if it is a DataFrame
                reader = PickleReader(io.BytesIO(self.buffer.getvalue()))
                data = reader.try_read_dataframe()
                if data is None:
                    data = reader.try_read_array()
                if data is None:
                    data = reader.t()
                if data is not None:
                    return data, False, True

            raise ExceptionUnsafePickle(cfg.MESSAGES["POTENTIAL_THREAT"])


def is_json_serializable(obj: Any) -> bool:
    """
    Determines if an object is JSON serializable.

    :param obj: The object to be tested for JSON serializability.
    :type obj: Any
    :return: A boolean value indicating whether the object is JSON
        serializable.
    :rtype: bool
    """
    try:
        json.dumps(obj)
        return True
    except (TypeError, OverflowError):
        return False
