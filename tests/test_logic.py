import pytest

from src.logic import process_data, pids_queue, output_queue


@pytest.fixture
def clear_queues() -> None:
    while not pids_queue.empty():
        pids_queue.get_nowait()
    while not output_queue.empty():
        output_queue.get_nowait()


def test_process_data_no_filename(clear_queues) -> None:
    process_data('')
    assert output_queue.qsize() == 0


