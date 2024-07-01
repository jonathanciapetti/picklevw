import pytest
from unittest.mock import patch, Mock
import tkinter as tk
from src.widgets import (
    set_options,
    PicklevwTkLoadButton,
    PicklevwTkThemeButton,
    PicklevwTkCanvas,
    PicklevwTkText,
    PicklevwTkFrame,
)


# Test for set_options
def test_set_options():
    with patch("src.widgets.set_option") as mock_set_option:
        set_options()
        mock_set_option.assert_any_call("display.max_rows", None)
        mock_set_option.assert_any_call("display.max_columns", None)


# Test for PicklevwTkLoadButton
@patch("tkinter.messagebox.showerror")
def test_picklevw_tk_load_button(mock_showerror):
    root = tk.Tk()
    try:
        btn = PicklevwTkLoadButton(root)
        assert btn.cget("bg") == "darkgreen"
        assert btn.cget("fg") == "white"
        assert btn.cget("text") == "Load"
    finally:
        root.destroy()
    mock_showerror.assert_not_called()


# Test for PicklevwTkThemeButton
@patch("tkinter.messagebox.showerror")
def test_picklevw_tk_theme_button(mock_showerror):
    root = tk.Tk()
    try:
        btn = PicklevwTkThemeButton(root)
        assert btn.cget("text") == "Switch to dark mode"
    finally:
        root.destroy()
    mock_showerror.assert_not_called()


# Test for PicklevwTkFrame
@patch("tkinter.messagebox.showerror")
def test_picklevw_tk_frame(mock_showerror):
    root = tk.Tk()
    try:
        frame = PicklevwTkFrame("test_frame", root)
        assert isinstance(frame.text, PicklevwTkText)
        assert isinstance(frame.vsb, tk.Scrollbar)
        assert isinstance(frame.linenumbers, PicklevwTkCanvas)
        mock_showerror.assert_not_called()
    finally:
        root.destroy()
