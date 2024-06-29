"""
Humble implementation of the Mediator pattern.
"""

from src.widgets import PicklevwTkLoadButton, PicklevwTkThemeButton, PicklevwTkFrame
from src.window import PicklevwTkWindow
from src.logic import start_process

import tkinter as tk

class Mediator:
    """ Mediator class to manage interactions between buttons and the main window. """

    def __init__(self, elements: tuple):
        self.elements = elements

        # Bind button press events to their respective handlers
        for elem in self.elements:
            try:
                if isinstance(elem, PicklevwTkWindow):
                    window = elem
                    elem.bind('<Key>', (lambda e: window.ctrl_events(e)))
                if isinstance(elem, PicklevwTkLoadButton):
                    elem.bind('<ButtonPress>', (lambda _: start_process()))
                elif isinstance(elem, PicklevwTkThemeButton):
                    elem.bind('<ButtonPress>', (lambda _: self.switch_theme(window)))
            except AttributeError as e:
                print(f"Error binding event for element {elem}: {e}")
            except Exception as e:
                print(f"Unexpected error: {e}")

    @staticmethod
    def switch_theme(window) -> None:
        """ Switches the theme of the text widget between light and dark mode. """
        try:
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
        except KeyError as e:
            tk.messagebox.showinfo(
                title="Error",
                message=f"Error switching theme, key not found: {e}"
            )
        except AttributeError as e:
            tk.messagebox.showinfo(
                title="Error",
                message=f"Error switching theme, attribute not found: {e}"
            )
        except Exception as e:
            tk.messagebox.showinfo(
                title="Error",
                message=f"Unexpected error switching theme: {e}"
            )

