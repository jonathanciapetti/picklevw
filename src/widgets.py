"""
This module defines custom tkinter widgets and their configurations.
"""

import tkinter as tk
from _tkinter import TclError
from typing import Any

from pandas import set_option


def set_options() -> None:
    """ Sets pandas display options to show all rows and columns. """
    set_option('display.max_rows', None)
    set_option('display.max_columns', None)


class PicklevwTkLoadButton(tk.Button):
    """Custom button with a specific color scheme for loading functionality."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            self.config(bg='darkgreen', fg='white', text="Load")
        except TclError as e:
            tk.messagebox.showinfo(
                title="Error",
                message=f"Error configuring PicklevwTkLoadButton: {e}"
            )
        except Exception as e:
            tk.messagebox.showinfo(
                title="Error",
                message=f"Unexpected error configuring PicklevwTkLoadButton: {e}"
            )


class PicklevwTkThemeButton(tk.Button):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            self.config(text="Switch to dark mode")
        except TclError as e:
            tk.messagebox.showinfo(
                title="Error",
                message=f"Error configuring PicklevwTkThemeButton: {e}"
            )
        except Exception as e:
            tk.messagebox.showinfo(
                title="Error",
                message=f"Unexpected error configuring PicklevwTkThemeButton: {e}"
            )


class PicklevwTkCanvas(tk.Canvas):
    """ Custom canvas to display line numbers for a text widget. """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.textwidget = None

    def attach(self, text_widget) -> None:
        """ Attaches a text widget to the canvas for displaying line numbers.

        :param text_widget: The text widget to attach.
        """
        self.textwidget = text_widget

    def redraw(self, *args) -> None:
        """ Redraw line numbers after each text update. """
        try:
            self.delete("all")
            i = self.textwidget.index("@0,0")
            while True:
                dline = self.textwidget.dlineinfo(i)
                if dline is None:
                    break
                y_positicn = dline[1]
                linenum = str(i).split(".", maxsplit=1)
                self.create_text(2, y_positicn, anchor="nw", text=linenum[0])
                i = self.textwidget.index(f"{i}+1line")
        except TclError as e:
            tk.messagebox.showinfo(
                title="Error",
                message=f"Error redrawing PicklevwTkCanvas: {e}"
            )
        except Exception as e:
            tk.messagebox.showinfo(
                title="Error",
                message=f"Unexpected error redrawing PicklevwTkCanvas: {e}"
            )


class PicklevwTkText(tk.Text):
    """ Custom text widget with an event proxy. TODO: undo functionality. """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, undo=True, maxundo=-1, autoseparators=True)
        self._orig = self._w + "_orig"
        try:
            self.tk.call("rename", self._w, self._orig)
            self.tk.createcommand(self._w, self._proxy)
            self.configure(background='white', foreground='black')
        except TclError as e:
            tk.messagebox.showinfo(
                title="Error",
                message=f"Error initializing PicklevwTkText: {e}"
            )
        except Exception as e:
            print(f"Unexpected error initializing PicklevwTkText: {e}")
            tk.messagebox.showinfo(
                title="Error",
                message=f"Error initializing PicklevwTkText: {e}"
            )

    def _proxy(self, *args) -> Any:
        """ Proxy method to intercept and handle widget commands.

        :param args: Arguments for the widget command.
        :return: Result of the widget command.
        """
        cmd = (self._orig,) + args
        try:
            result = self.tk.call(cmd)
        except TclError as e:
            tk.messagebox.showinfo(
                title="Error",
                message=f"Error in PicklevwTkText proxy method: {e}"
            )
            result = ''  # Hotfix for "_tkinter.TclError: nothing to undo". TODO: fix it properly.
        except Exception as e:
            tk.messagebox.showinfo(
                title="Error",
                message=f"Unexpected error in PicklevwTkText proxy method: {e}"
            )
            result = ''

        # Generate an event if something was added or deleted, or the cursor position has changed:
        if (
                args[0] in ("insert", "replace", "delete") or
                args[0:3] == ("mark", "set", "insert") or
                args[0:2] in (
                ("xview", "moveto"), ("xview", "scroll"),
                ("yview", "moveto"), ("yview", "scroll")
        )
        ):
            self.event_generate("<<Change>>", when="tail")

        return result


class PicklevwTkFrame(tk.Frame):
    """ Custom frame containing a text widget with line numbers and a vertical scrollbar. """

    def __init__(self, name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            self.receive = None
            self.text = PicklevwTkText(self)
            self.vsb = tk.Scrollbar(self, orient="vertical", command=self.text.yview)
            self.text.configure(yscrollcommand=self.vsb.set)

            self.linenumbers = PicklevwTkCanvas(self, width=30)
            self.linenumbers.attach(self.text)

            # These bindings cannot be managed by the Mediator,
            # because they are defined at the object initialization:
            self.text.bind("<<Change>>", self._on_change)
            self.text.bind("<Configure>", self._on_change)

            self.vsb.pack(side="right", fill="y")
            self.linenumbers.pack(side="left", fill="y")
            self.text.pack(side="right", fill="both", expand=True)

            self.name = name
        except TclError as e:
            tk.messagebox.showinfo(
                title="Error",
                message=f"Error initializing PicklevwTkFrame: {e}"
            )
        except Exception as e:
            tk.messagebox.showinfo(
                title="Error",
                message=f"Unexpected error initializing PicklevwTkFrame: {e}"
            )

    def _on_change(self, event) -> None:
        """ Handles the change event to redraw line numbers.

        :param event: The event object.
        """
        try:
            self.linenumbers.redraw()
        except TclError as e:
            tk.messagebox.showinfo(
                title="Error",
                message=f"Error in PicklevwTkFrame _on_change method: {e}"
            )
        except Exception as e:
            tk.messagebox.showinfo(
                title="Error",
                message=f"Unexpected error in PicklevwTkFrame _on_change method: {e}"
            )
