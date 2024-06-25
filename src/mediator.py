"""
This module defines the implementation of the Mediator pattern (from the Gang of 4 book).
It is just an attempt, so it must be assumed as flawed.
"""

from src.widgets import LoadButton, ThemeButton
from src.window import CustomWindow
from src.logic import start_process


class Mediator:
    """Mediator class to manage interactions between buttons and the main window."""

    def __init__(self, elements: list, window: CustomWindow):
        self.elements = elements
        self.button_receivers = []
        self.window_ = window

        # Bind key events in the window to a control event handler
        self.window_.bind("<Key>", lambda e: self.window_.ctrl_events(e))

        # Bind button press events to their respective handlers
        for elem in self.elements:
            if isinstance(elem, LoadButton):
                elem.bind('<ButtonPress>', (lambda _: start_process()))
            elif isinstance(elem, ThemeButton):
                elem.bind('<ButtonPress>', (lambda _: self.switch_theme()))

    def switch_theme(self):
        """Switches the theme of the text widget between light and dark modes."""

        current_bg = self.window_.widgets["example"].text["background"]
        if current_bg == "white":
            self.window_.widgets["example"].text.configure(
                background="black",
                foreground="white",
            )
            self.window_.widgets["btn_theme"]["text"] = "Switch to light mode"
        else:
            self.window_.widgets["example"].text.configure(
                background="white",
                foreground="black",
            )
            self.window_.widgets["btn_theme"]["text"] = "Switch to dark mode"
