import pytest
from unittest.mock import patch, Mock
import tkinter as tk
from src.factory import WidgetFactory
from src.window import PicklevwTkWindow


@patch("tkinter.messagebox.showerror")
def test_update_lbl_header(mock_showerror):
    window = PicklevwTkWindow()
    header = window.update_lbl_header("testfile.pkl")
    assert header == "File:  testfile.pkl"
    mock_showerror.assert_not_called()


@patch("tkinter.messagebox.showerror")
def test_setup_cols(mock_showerror):
    window = PicklevwTkWindow()
    window.frames = {
        "btn_load_frame": Mock(),
        "lbl_header_frame": Mock(),
        "lbl_search_frame": Mock(),
        "searchbox_frame": Mock(),
        "example_frame": Mock(),
    }
    window.setup_cols()
    for frame in window.frames.values():
        frame.grid_columnconfigure.assert_called()
    mock_showerror.assert_not_called()


@patch("tkinter.messagebox.showerror")
def test_setup_rows(mock_showerror):
    window = PicklevwTkWindow()
    window.frames = {
        "example_frame": Mock(),
        "lbl_footer_frame": Mock(),
    }
    window.setup_rows()
    for frame in window.frames.values():
        frame.grid_rowconfigure.assert_called()
    mock_showerror.assert_not_called()


@patch("tkinter.messagebox.showerror")
def test_setup_frames(mock_showerror):
    window = PicklevwTkWindow()
    window.setup_frames()
    for frame_name in [
        "lbl_header_frame",
        "btn_load_frame",
        "btn_theme_frame",
        "lbl_search_frame",
        "searchbox_frame",
        "lbl_footer_frame",
        "example_frame",
    ]:
        assert frame_name in window.frames
        assert isinstance(window.frames[frame_name], tk.Frame)
    mock_showerror.assert_not_called()


