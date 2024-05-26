"""
foobar
"""

from .custom_widgets import LoadButton, ThemeButton
from .custom_window import CustomWindow
from .logic import start_process


class Mediator:
    """
    xyzt
    """

    def __init__(self, elements: list, window: CustomWindow):

        self.elements = elements
        self.button_receivers = []
        self.window_ = window

        self.window_.bind("<Key>", lambda e: self.window_.ctrl_events(e))

        for elem in self.elements:
            if isinstance(elem, LoadButton):
                elem.bind('<ButtonPress>', (lambda _: start_process()))
            elif isinstance(elem, ThemeButton):
                elem.bind('<ButtonPress>', (lambda _: self.switch_theme()))

    def switch_theme(self):
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
