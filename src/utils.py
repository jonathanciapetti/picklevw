import io
import gzip
import json
import pickle
import re
from typing import Any, Tuple, Optional, Union

import pandas as pd
from fickling.analysis import check_safety
from fickling.exception import UnsafeFileError
from fickling.fickle import Pickled
import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile

import config as cfg
from exceptions import ExceptionUnsafePickle


class PickleSecurityChecker:
    SEVERITY_THRESHOLD = 1

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
        if severity.value[0] > self.SEVERITY_THRESHOLD:
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
                df = reader.try_read_dataframe()
                if df is not None:
                    return df, False, True

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

def return_load_error():
    st.warning(cfg.MESSAGES["GENERIC_LOAD_ERROR"])
    return

def get_pandas_data(obj):
    return {
        "type": "series",
        "name": obj.name or 'unnamed',
        "length": len(obj),
        "data": obj.to_frame(),
        "is_numeric": pd.api.types.is_numeric_dtype(obj),
    }

def get_pandas_df_data(obj):
    return {
        "type": "dataframe",
        "data": obj,
        "summary": cfg.MESSAGES["row_col_summary"].format(rows=len(obj), cols=len(obj.columns))
    }

def get_json_serializable_obj_data(obj, were_spared_objs):
    formatted = json.dumps(obj, indent=4)
    if were_spared_objs:
        formatted = re.sub(r'^"(.*)"$', r"\1", formatted, flags=re.MULTILINE)
    return {
        "type": "json",
        "content": formatted
    }

def get_pandas_series_data(obj):
    return {
        "type": "series",
        "name": obj.name or 'unnamed',
        "length": len(obj),
        "data": obj.to_frame(),
        "is_numeric": pd.api.types.is_numeric_dtype(obj),
    }

def analyze_object_for_display(obj, were_spared_objs, is_dataframe):
    """
    Analyzes the provided object to determine its type and prepares appropriate data
    for display based on its characteristics. The function supports analysis for
    Pandas DataFrames, Series, JSON-serializable objects, and handles cases where
    the object is None or not JSON-serializable. For DataFrame and Series, respective
    utility functions are used to extract displayable content.

    :param obj: The object to analyze.
    :param were_spared_objs: Tracks objects that were spared during the JSON serialization
        process to avoid redundancy or circular references.
    :param is_dataframe: Boolean indicating whether the object should be treated as a
        DataFrame.
    :return: A dictionary containing details about the analyzed object for display purposes,
        or a warning message and type if the object is not JSON-serializable.
    """
    if not is_dataframe and obj is None:
        return return_load_error()

    if isinstance(obj, pd.DataFrame):
        return get_pandas_df_data(obj)

    elif isinstance(obj, pd.Series):
        return get_pandas_series_data(obj)

    elif is_json_serializable(obj):
        return get_json_serializable_obj_data(obj, were_spared_objs)
    else:
        return {
            "type": "warning",
            "message": cfg.MESSAGES["NOT_JSON_WARNING"]
        }

def render_display_plan(plan):
    """
    Render the given display plan in the Streamlit application. The function processes the
    input plan based on its type and displays the corresponding content in an appropriate
    format using Streamlit components.

    :param plan: A dictionary that specifies the display type and associated content.
    :return: None
    """
    st.markdown(cfg.MESSAGES["CONTENT_DISPLAY"])

    if plan["type"] == "dataframe":
        st.write(plan.get("summary"))
        st.dataframe(plan.get("data"))

    elif plan.get("type") == "series":
        st.write(f"Pandas or NumPy Series: **{plan['name']}**, {plan['length']} elements")
        st.dataframe(plan.get("data"))
        if plan["is_numeric"]:
            st.markdown(cfg.MESSAGES["CHART"])
            series = plan["data"].squeeze()
            st.line_chart(series)

    elif plan["type"] == "json":
        st.code(plan["content"], language="json")

    elif plan["type"] == "warning":
        st.warning(plan["message"])
