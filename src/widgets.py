"""
This module defines custom tkinter widgets and their configurations.
"""

import tkinter as tk
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
        self.config(bg='darkgreen', fg='white', text="Load")


class PicklevwTkThemeButton(tk.Button):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config(text="Switch to dark mode")


class PicklevwTkCanvas(tk.Canvas):
    """ Custom canvas to display line numbers for a text widget. """

    def __init__(self, *args, **kwargs):
        tk.Canvas.__init__(self, *args, **kwargs)
        self.textwidget = None

    def attach(self, text_widget) -> None:
        """ Attaches a text widget to the canvas for displaying line numbers.

        :param text_widget: The text widget to attach.
        """
        self.textwidget = text_widget

    def redraw(self, *args) -> None:
        """ Redraw line numbers after each text update. """

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


class PicklevwTkText(tk.Text):
    """ Custom text widget with an event proxy. TODO: undo functionality. """

    def __init__(self, *args, **kwargs):
        tk.Text.__init__(self, *args, **kwargs, undo=True, maxundo=1)
        self._orig = self._w + "_orig"
        self.tk.call("rename", self._w, self._orig)
        self.tk.createcommand(self._w, self._proxy)
        self.configure(background='white', foreground='black')

    def _proxy(self, *args) -> Any:
        """ Proxy method to intercept and handle widget commands.

        :param args: Arguments for the widget command.
        :return: Result of the widget command.
        """
        # Let the actual widget perform the requested action:
        cmd = (self._orig,) + args
        result = self.tk.call(cmd)

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
        tk.Frame.__init__(self, *args, **kwargs)
        self.receive = None
        self.text = PicklevwTkText(self)
        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.text.yview)
        self.text.configure(yscrollcommand=self.vsb.set)
        self.linenumbers = PicklevwTkCanvas(self, width=30)
        self.linenumbers.attach(self.text)
        self.vsb.pack(side="right", fill="y")
        self.linenumbers.pack(side="left", fill="y")
        self.text.pack(side="right", fill="both", expand=True)
        self.text.bind("<<Change>>", self._on_change)
        self.text.bind("<Configure>", self._on_change)
        self.name = name

    def _on_change(self, event) -> None:
        """ Handles the change event to redraw line numbers.

        :param event: The event object.
        """
        self.linenumbers.redraw()
