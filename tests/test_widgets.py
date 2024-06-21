import pytest
import tkinter as tk
from pyvirtualdisplay import Display
from pandas import get_option
from src.widgets import set_options, LoadButton, ThemeButton, Element, TextLineNumbers, CustomText, \
    Example


@pytest.fixture(scope='function')
def display():
    display = Display(visible=0, size=(800, 600))
    display.start()
    yield
    display.stop()


def test_set_options():
    set_options()
    assert get_option('display.max_rows') is None
    assert get_option('display.max_columns') is None


def test_load_button_initialization(display):
    root = tk.Tk()
    button = LoadButton(master=root, text="Load")
    assert button.cget('bg') == 'darkgreen'
    assert button.cget('fg') == 'white'
    assert button.cget('text') == 'Load'
    root.destroy()


def test_theme_button_initialization(display):
    root = tk.Tk()
    button = ThemeButton(master=root, text="Theme")
    assert button.cget('text') == 'Theme'
    root.destroy()


def test_element_placement(display):
    root = tk.Tk()
    frame = tk.Frame(master=root)
    label = tk.Label(master=frame, text="Test")
    element = Element(widget=label, master=frame, i=0, j=0, padx=5, pady=5)
    info = label.grid_info()
    assert info['row'] == 0
    assert info['column'] == 0
    assert info['padx'] == 5
    assert info['pady'] == 5
    root.destroy()


def test_text_line_numbers_attachment(display):
    root = tk.Tk()
    text_widget = tk.Text(master=root)
    text_line_numbers = TextLineNumbers(master=root)
    text_line_numbers.attach(text_widget)
    assert text_line_numbers.textwidget == text_widget
    root.destroy()


def test_text_line_numbers_redraw(display):
    root = tk.Tk()
    text_widget = tk.Text(master=root)
    text_line_numbers = TextLineNumbers(master=root)
    text_line_numbers.attach(text_widget)
    text_widget.insert("1.0", "Line 1\nLine 2\nLine 3")
    text_line_numbers.redraw()
    assert text_line_numbers.find_all()
    root.destroy()


def test_custom_text_initialization(display):
    root = tk.Tk()
    custom_text = CustomText(master=root)
    assert custom_text.cget('maxundo') == 1
    assert custom_text.cget('background') == 'white'
    assert custom_text.cget('foreground') == 'black'
    root.destroy()


def test_custom_text_proxy(display):
    root = tk.Tk()
    custom_text = CustomText(master=root)
    custom_text.insert("1.0", "Test")
    assert custom_text.get("1.0", "end-1c") == "Test"
    custom_text.delete("1.0", "end")
    assert custom_text.get("1.0", "end-1c") == ""
    root.destroy()


def test_example_initialization(display):
    root = tk.Tk()
    example = Example(master=root, name="output_box")
    assert isinstance(example.text, CustomText)
    assert isinstance(example.vsb, tk.Scrollbar)
    assert isinstance(example.linenumbers, TextLineNumbers)
    root.destroy()


def test_example_on_change_event(display):
    root = tk.Tk()
    example = Example(master=root, name="output_box")
    example.text.insert("1.0", "Line 1\nLine 2\nLine 3")
    example._on_change(None)
    assert example.linenumbers.find_all()
    root.destroy()
