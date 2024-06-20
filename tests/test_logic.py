import pytest
from unittest.mock import patch, mock_open, MagicMock
import pickle
from pandas import DataFrame
from src.logic import process_data, start_process, terminate_all_processes, pids_queue, output_queue


@pytest.fixture
def clear_queues():
    while not pids_queue.empty():
        pids_queue.get_nowait()
    while not output_queue.empty():
        output_queue.get_nowait()
    yield
    while not pids_queue.empty():
        pids_queue.get_nowait()
    while not output_queue.empty():
        output_queue.get_nowait()


def test_process_data_no_filename(clear_queues):
    process_data('')
    assert output_queue.qsize() == 0


# @patch('builtins.open', new_callable=mock_open, read_data=b'\x1f\x8b')
# @patch('gzip.open')
# @patch('pandas.read_pickle')
# def test_process_data_gzip(mock_read_pickle, mock_gzip_open, mock_file, clear_queues):
#     mock_read_pickle.return_value = DataFrame()
#     mock_gzip_open.return_value = mock_file
#     process_data('test.gz')
#     message = output_queue.get_nowait()
#     assert message['status'] == 'completed'
#     assert message['filename'] == 'test.gz'
#     assert isinstance(message['output'], str)


# @patch('builtins.open', new_callable=mock_open, read_data=b'notgzip')
# @patch('pandas.read_pickle')
# def test_process_data_pickle(mock_read_pickle, mock_file, clear_queues):
#     mock_read_pickle.return_value = DataFrame()
#     process_data('test.pkl')
#     message = output_queue.get_nowait()
#     assert message['status'] == 'completed'
#     assert message['filename'] == 'test.pkl'
#     assert isinstance(message['output'], str)


@patch('builtins.open', new_callable=mock_open)
def test_process_data_file_not_found(mock_file, clear_queues):
    mock_file.side_effect = FileNotFoundError
    process_data('notfound.pkl')
    assert output_queue.qsize() == 1


@patch('builtins.open', new_callable=mock_open, read_data=b'notgzip')
@patch('pandas.read_pickle')
def test_process_data_unicode_error(mock_read_pickle, mock_file, clear_queues):
    mock_read_pickle.side_effect = UnicodeDecodeError("codec", b"", 0, 1, "reason")
    process_data('unicode_error.pkl')
    assert output_queue.qsize() == 1


@patch('builtins.open', new_callable=mock_open, read_data=b'notgzip')
@patch('pandas.read_pickle')
def test_process_data_unpickling_error(mock_read_pickle, mock_file, clear_queues):
    mock_read_pickle.side_effect = pickle.UnpicklingError
    process_data('unpickling_error.pkl')
    assert output_queue.qsize() == 1


# @patch('psutil.Process')
# @patch('tkinter.filedialog.askopenfilename', return_value='test.pkl')
# @patch('multiprocessing.Process')
# def test_start_process(mock_process_class, mock_askopenfilename, mock_psutil_process, clear_queues):
#     mock_process_instance = MagicMock()
#     mock_process_class.return_value = mock_process_instance
#
#     start_process()
#
#     mock_askopenfilename.assert_called_once()
#     mock_process_instance.start.assert_called_once()
#     assert pids_queue.qsize() == 1


# @patch('psutil.Process')
# def test_terminate_all_processes(mock_psutil_process, clear_queues):
#     pids_queue.put(12345)
#     mock_proc_instance = MagicMock()
#     mock_psutil_process.return_value = mock_proc_instance
#
#     terminate_all_processes()
#
#     mock_psutil_process.assert_called_once_with(12345)
#     mock_proc_instance.terminate.assert_called_once()
#     assert pids_queue.qsize() == 0
