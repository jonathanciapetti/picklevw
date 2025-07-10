import pytest
import gzip
import pickle
import pandas as pd
from io import BytesIO
from unittest.mock import MagicMock, patch
from types import SimpleNamespace


# Sample test data
sample_obj = {"key": "value"}
sample_df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})


# Utility to simulate Streamlit's UploadedFile
def create_mock_uploaded_file(data: bytes):
    mock_file = MagicMock()
    mock_file.read.return_value = data
    mock_file.seek.side_effect = lambda x: None
    return mock_file


@pytest.fixture
def raw_pickle_data():
    return pickle.dumps(sample_obj)


@pytest.fixture
def raw_pickle_df():
    buffer = BytesIO()
    sample_df.to_pickle(buffer)
    return buffer.getvalue()


@pytest.fixture
def gzip_pickle_data(raw_pickle_data):
    return gzip.compress(raw_pickle_data)


@patch("fickling.fickle.Pickled.load")
@patch("fickling.analysis.check_safety")
def test_pickle_loader_safe(mock_check_safety, mock_pickled_load, raw_pickle_data):
    from src.utils import PickleLoader
    from fickling.analysis import Severity

    mock_check_safety.return_value = SimpleNamespace(severity=Severity.LIKELY_SAFE)
    mock_pickled_load.return_value = MagicMock()

    uploaded_file = create_mock_uploaded_file(raw_pickle_data)
    loader = PickleLoader(uploaded_file)
    obj, multiple, is_df = loader.load()

    assert obj == sample_obj
    assert multiple is False
    assert is_df is False


@patch("src.utils.cfg")
@patch("src.utils.PickleSecurityChecker.ensure_safe")
def test_pickle_loader_dataframe(mock_ensure_safe, mock_cfg, raw_pickle_df):
    from src.utils import PickleLoader
    from fickling.exception import UnsafeFileError

    # simulate unsafe pickle
    mock_ensure_safe.side_effect = UnsafeFileError(info="test", filepath="file")
    mock_cfg.MESSAGES = {"POTENTIAL_THREAT": "threat detected"}

    uploaded_file = create_mock_uploaded_file(raw_pickle_df)
    loader = PickleLoader(uploaded_file, allow_unsafe_file=True)

    obj, multiple, is_df = loader.load()

    pd.testing.assert_frame_equal(obj, sample_df)
    assert multiple is False
    assert is_df is True


@patch("src.utils.cfg")
@patch("src.utils.PickleSecurityChecker.ensure_safe")
def test_pickle_loader_unsafe(mock_ensure_safe, mock_cfg):
    from src.utils import PickleLoader, ExceptionUnsafePickle
    from fickling.exception import UnsafeFileError

    mock_ensure_safe.side_effect = UnsafeFileError(
        info="Test unsafe file", filepath="test.pickle"
    )
    mock_cfg.MESSAGES = {"POTENTIAL_THREAT": "threat detected"}

    dummy_data = b"not_really_pickle"
    uploaded_file = create_mock_uploaded_file(dummy_data)

    loader = PickleLoader(uploaded_file, allow_unsafe_file=False)

    with pytest.raises(ExceptionUnsafePickle) as e:
        loader.load()

    assert "threat" in str(e.value)


def test_is_json_serializable():
    from src.utils import is_json_serializable

    assert is_json_serializable({"key": "value"})
    assert not is_json_serializable({1, 2, 3})  # set is not JSON serializable