from pickle import UnpicklingError
from unittest.mock import mock_open
import gzip
from io import BytesIO

from src.logic import process_data, output_queue


def test_process_data_gzip(mocker):
    filename = "test.pkl.gz"
    mocker.patch(
        "builtins.open",
        new_callable=mock_open,
        read_data=BytesIO(gzip.compress(b"content")).read(),
    )
    mocker.patch("src.logic.read_pickle", return_value={"key": "value"})

    process_data(filename)

    message = output_queue.get()
    assert message["status"] == "completed"
    assert message["filename"] == filename
    assert "key" in message["output"]


def test_process_data_pickle(mocker):
    filename = "test.pkl"
    mocker.patch("builtins.open", new_callable=mock_open, read_data=b"content")
    mocker.patch("src.logic.read_pickle", return_value={"key": "value"})

    process_data(filename)

    message = output_queue.get()
    assert message["status"] == "completed"
    assert message["filename"] == filename
    assert "key" in message["output"]


def test_process_data_file_not_found(mocker):
    filename = "missing.pkl"
    mocker.patch("builtins.open", side_effect=FileNotFoundError("File not found"))

    process_data(filename)

    message = output_queue.get()
    assert message["status"] == "failed"
    assert "File not found" in message["messagebox"]


def test_process_data_unicode_error(mocker):
    filename = "invalid.pkl"
    mocker.patch("builtins.open", new_callable=mock_open, read_data=b"\x80\x03}")
    mocker.patch(
        "src.logic.read_pickle",
        side_effect=UnicodeDecodeError("utf-8", b"", 0, 1, "invalid start byte"),
    )

    process_data(filename)

    message = output_queue.get()
    assert message["status"] == "failed"
    assert "Not a text pickle file" in message["messagebox"]


def test_process_data_unpickling_error(mocker):
    filename = "invalid.pkl"
    mocker.patch("builtins.open", new_callable=mock_open, read_data=b"\x80\x03}")
    mocker.patch(
        "src.logic.read_pickle", side_effect=UnpicklingError("Unpickling error")
    )

    process_data(filename)

    message = output_queue.get()
    assert message["status"] == "failed"
    assert "Unpickling error" in message["messagebox"]


def test_process_data_generic_error(mocker):
    filename = "invalid.pkl"
    mocker.patch("builtins.open", new_callable=mock_open, read_data=b"\x80\x03}")
    mocker.patch("src.logic.read_pickle", side_effect=Exception("Generic error"))

    process_data(filename)

    message = output_queue.get()
    assert message["status"] == "failed"
    assert "Generic error" in message["messagebox"]
