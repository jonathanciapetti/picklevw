import io
import gzip
import pickle
import pytest

from src.utils import load_pickle, is_json_serializable


@pytest.fixture
def plain_pickle_file():
    # Simulate a pickle file that contains the integer 3
    data = 3
    expected = {0, 1, 2}
    buf = io.BytesIO()
    pickle.dump(data, buf)
    buf.seek(0)
    return buf, expected


@pytest.fixture
def gzip_pickle_file():
    # Simulate a gzipped pickle file that contains the integer 2
    data = 2
    expected = {0, 1}
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb") as f:
        pickle.dump(data, f)
    buf.seek(0)
    return buf, expected


def test_load_pickle_plain(plain_pickle_file):
    buf, expected = plain_pickle_file
    result = load_pickle(buf)
    assert result == expected


def test_load_pickle_gzip(gzip_pickle_file):
    buf, expected = gzip_pickle_file
    result = load_pickle(buf)
    assert result == expected


@pytest.mark.parametrize(
    "obj,expected",
    [
        ({"a": 1}, True),
        ([1, 2, 3], True),
        ("text", True),
        (object(), False),  # not serializable
        (float("inf"), True),
    ],
)
def test_is_json_serializable(obj, expected):
    assert is_json_serializable(obj) == expected
