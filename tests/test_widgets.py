from unittest.mock import patch,
import tkinter as tk
from src.widgets import (
    set_options,
    PicklevwTkLoadButton,
    PicklevwTkThemeButton,
    PicklevwTkCanvas,
    PicklevwTkText,
    PicklevwTkFrame,
)


def test_set_options():
    with patch("src.widgets.set_option") as mock_set_option:
        set_options()
        mock_set_option.assert_any_call("display.max_rows", None)
        mock_set_option.assert_any_call("display.max_columns", None)


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


@patch("tkinter.messagebox.showerror")
def test_picklevw_tk_theme_button(mock_showerror):
    root = tk.Tk()
    try:
        btn = PicklevwTkThemeButton(root)
        assert btn.cget("text") == "Switch to dark mode"
    finally:
        root.destroy()
    mock_showerror.assert_not_called()


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

# @patch("tkinter.messagebox.showerror")
# def test_picklevw_tk_canvas(mock_showerror):
#     root = tk.Tk()
#     try:
#         canvas = PicklevwTkCanvas(root)
#         mock_text_widget = Mock()
#         canvas.attach(mock_text_widget)
#         assert canvas.textwidget == mock_text_widget
#         canvas.redraw()
#         mock_showerror.assert_not_called()
#     finally:
#         root.destroy()


# @patch("tkinter.messagebox.showerror")
# @patch("tkinter.Text.tk.call")
# def test_picklevw_tk_text(mock_tk_call, mock_showerror):
#     root = tk.Tk()
#     try:
#         text = PicklevwTkText(root)
#         assert text.cget("background") == "white"
#         assert text.cget("foreground") == "black"
#         mock_tk_call.assert_any_call("rename", text._w, text._orig)
#         mock_tk_call.assert_any_call(text._w, text._proxy)
#     finally:
#         root.destroy()
#     mock_showerror.assert_not_called()
