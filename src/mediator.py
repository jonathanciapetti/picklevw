"""
Humble implementation of the Mediator pattern.
"""

from src.widgets import PicklevwTkLoadButton, PicklevwTkThemeButton
from src.window import PicklevwTkWindow
from src.logic import start_process

import tkinter as tk


class Mediator:
    """Mediator class that cares to bind events to handlers, for each widget."""

    def __init__(self, *args):

        for elem in args:
            try:
                if isinstance(elem, PicklevwTkWindow):
                    window = elem
                    elem.bind("<Key>", (lambda e: window.ctrl_events(e)))
                if isinstance(elem, PicklevwTkLoadButton):
                    elem.bind("<ButtonPress>", (lambda _: start_process()))
                elif isinstance(elem, PicklevwTkThemeButton):
                    elem.bind("<ButtonPress>", (lambda _: self.switch_theme(window)))
            except AttributeError as e:
                tk.messagebox.showerror(
                    title="Error",
                    message=f"Error binding event for element {elem}: {e}",
                )
            except Exception as e:
                tk.messagebox.showerror(title="Error", message=f"Unexpected error: {e}")

    @staticmethod
    def switch_theme(window: PicklevwTkWindow) -> None:
        """Switches the theme of the text widget between light and dark mode."""
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
            tk.messagebox.showerror(
                title="Error", message=f"Error switching theme, key not found: {e}"
            )
        except AttributeError as e:
            tk.messagebox.showerror(
                title="Error",
                message=f"Error switching theme, attribute not found: {e}",
            )
        except Exception as e:
            tk.messagebox.showerror(
                title="Error", message=f"Unexpected error switching theme: {e}"
            )
