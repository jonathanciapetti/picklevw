"""
Humble implementation of the Mediator pattern.
"""

from src.widgets import PicklevwTkLoadButton, PicklevwTkThemeButton, PicklevwTkFrame
from src.window import PicklevwTkWindow
from src.logic import start_process


class Mediator:
    """ Mediator class to manage interactions between buttons and the main window. """

    def __init__(self, elements: tuple):
        self.elements = elements

        # Bind button press events to their respective handlers
        for elem in self.elements:
            if isinstance(elem, PicklevwTkWindow):
                window = elem
                elem.bind('<Key>', (lambda e: window.ctrl_events(e)))
            if isinstance(elem, PicklevwTkLoadButton):
                elem.bind('<ButtonPress>', (lambda _: start_process()))
            elif isinstance(elem, PicklevwTkThemeButton):
                elem.bind('<ButtonPress>', (lambda _: self.switch_theme(window)))

    @staticmethod
    def switch_theme(window) -> None:
        """ Switches the theme of the text widget between light and dark mode. """

        current_bg = window.widgets["picklevw_tk_frame"].text["background"]
        if current_bg == "white":
            window.widgets["picklevw_tk_frame"].text.configure(
                background="black",
                foreground="white",
            )
            window.widgets["btn_theme"]["text"] = "Switch to light mode"
        else:
            window.widgets["picklevw_tk_frame"].text.configure(
                background="white",
                foreground="black",
            )
            window.widgets["btn_theme"]["text"] = "Switch to dark mode"
