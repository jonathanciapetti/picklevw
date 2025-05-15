import io
import gzip
import pickle
import pytest

from src.utils import load_pickle, is_json_serializable


@pytest.fixture
def plain_pickle_file():
    # Simulate a pickle file that contains multiple objects: 0, 1, 2
    expected = "0, 1, 2"
    is_multiple = True
    buf = io.BytesIO()
    for i in range(3):
        pickle.dump(i, buf)
    buf.seek(0)
    return buf, expected, is_multiple


@pytest.fixture
def gzip_pickle_file():
    # Simulate a gzipped pickle file that contains one object: 0
    expected = 0
    is_multiple = False
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb") as f:
        pickle.dump(expected, f)
    buf.seek(0)
    return buf, expected, is_multiple


def test_load_pickle_plain(plain_pickle_file):
    buf, expected, is_multiple = plain_pickle_file
    result, result_multiple = load_pickle(buf)
    assert result == expected
    assert result_multiple == is_multiple


def test_load_pickle_gzip(gzip_pickle_file):
    buf, expected, is_multiple = gzip_pickle_file
    result, result_multiple = load_pickle(buf)
    assert result == expected
    assert result_multiple == is_multiple


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
