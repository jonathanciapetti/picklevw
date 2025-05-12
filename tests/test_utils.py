import io
import gzip
import pickle
import pytest

from src.utils import load_pickle, is_json_serializable


@pytest.fixture
def plain_pickle_file():
    data = {"key": "value"}
    buf = io.BytesIO()
    pickle.dump(data, buf)
    buf.seek(0)
    return buf, data


@pytest.fixture
def gzip_pickle_file():
    data = [1, 2, 3]
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb") as f:
        pickle.dump(data, f)
    buf.seek(0)
    return buf, data


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
