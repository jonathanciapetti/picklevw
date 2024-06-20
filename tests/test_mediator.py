import pytest
import tkinter as tk
from unittest.mock import Mock
from src.widgets import LoadButton, ThemeButton
from src.window import CustomWindow
from src.mediator import Mediator


@pytest.fixture
def setup_tkinter():
    root = tk.Tk()
    yield root
    root.destroy()


@pytest.fixture
def custom_window(setup_tkinter):
    window = CustomWindow()
    window.widgets["example"] = Mock()
    window.widgets["example"].text = tk.Text(window)
    window.widgets["btn_theme"] = LoadButton(window, text="Switch to dark mode")
    return window


def test_mediator_initialization(setup_tkinter, custom_window):
    load_button = LoadButton(custom_window, text="Load")
    theme_button = ThemeButton(custom_window, text="Theme")
    elements = [load_button, theme_button]

    mediator = Mediator(elements, custom_window)

    assert mediator.elements == elements
    assert mediator.window_ == custom_window
    # assert load_button.bindtags()[-1] == '<ButtonPress>'
    # assert theme_button.bindtags()[-1] == '<ButtonPress>'
    # assert custom_window.bindtags()[-1] == '<Key>'


def test_switch_theme(setup_tkinter, custom_window):
    load_button = LoadButton(custom_window, text="Load")
    theme_button = ThemeButton(custom_window, text="Switch to dark mode")
    elements = [load_button, theme_button]

    mediator = Mediator(elements, custom_window)

    # Set initial theme to light mode
    custom_window.widgets["example"].text.configure(background="white", foreground="black")

    # Switch to dark mode
    mediator.switch_theme()
    assert custom_window.widgets["example"].text.cget("background") == "black"
    assert custom_window.widgets["example"].text.cget("foreground") == "white"
    assert custom_window.widgets["btn_theme"].cget("text") == "Switch to light mode"

    # Switch back to light mode
    mediator.switch_theme()
    assert custom_window.widgets["example"].text.cget("background") == "white"
    assert custom_window.widgets["example"].text.cget("foreground") == "black"
    assert custom_window.widgets["btn_theme"].cget("text") == "Switch to dark mode"
