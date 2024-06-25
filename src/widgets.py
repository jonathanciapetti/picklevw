"""
foobar
"""
import tkinter as tk
from pandas import set_option


def set_options() -> None:
    """

    :return:
    :rtype:
    """
    set_option('display.max_rows', None)
    set_option('display.max_columns', None)


class LoadButton(tk.Button):
    """ bbb
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config(bg='darkgreen', fg='white')


class ThemeButton(tk.Button):
    """ Button for the light/dark theme switch. """
    ...


class Element:
    """ ccc
    """

    def __init__(self, widget: tk.Widget, master, i, j, padx, pady):
        self._widget = widget
        self._widget.master = master
        self._widget.grid(row=i, column=j, padx=padx, pady=pady)

    def grid(self):
        """ abcde
        :return:
        :rtype:
        """
        return self._widget.grid()


class PicklevwTkinterCanvas(tk.Canvas):
    """ ddd
    """

    def __init__(self, *args, **kwargs):
        tk.Canvas.__init__(self, *args, **kwargs)
        self.textwidget = None

    def attach(self, text_widget):
        """ abcde
        :param text_widget:
        :type text_widget:
        :return:
        :rtype:
        """
        self.textwidget = text_widget

    def redraw(self, *args):
        '''redraw line numbers'''
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


class PicklevwTkinterText(tk.Text):
    """ ddd
    """

    def __init__(self, *args, **kwargs):
        tk.Text.__init__(self, *args, **kwargs, undo=True, maxundo=1)

        # create a proxy for the underlying widget
        self._orig = self._w + "_orig"
        self.tk.call("rename", self._w, self._orig)
        self.tk.createcommand(self._w, self._proxy)
        self.configure(background='white', foreground='black')

    def _proxy(self, *args):
        """ abcde
        :param args:
        :type args:
        :return:
        :rtype:
        """
        # let the actual widget perform the requested action
        cmd = (self._orig,) + args
        result = self.tk.call(cmd)

        # generate an event if something was added or deleted,
        # or the cursor position changed
        if (
                args[0] in ("insert", "replace", "delete") or
                args[0:3] == ("mark", "set", "insert") or
                args[0:2] == ("xview", "moveto") or
                args[0:2] == ("xview", "scroll") or
                args[0:2] == ("yview", "moveto") or
                args[0:2] == ("yview", "scroll")
        ):
            self.event_generate("<<Change>>", when="tail")

        # return what the actual widget returned
        return result


class PicklevwTkinterFrame(tk.Frame):
    """
    eee
    """

    def __init__(self, name, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        self.receive = None
        self.text = PicklevwTkinterText(self)
        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.text.yview)
        self.text.configure(yscrollcommand=self.vsb.set)
        self.linenumbers = PicklevwTkinterCanvas(self, width=30)
        self.linenumbers.attach(self.text)
        self.vsb.pack(side="right", fill="y")
        self.linenumbers.pack(side="left", fill="y")
        self.text.pack(side="right", fill="both", expand=True)
        self.text.bind("<<Change>>", self._on_change)
        self.text.bind("<Configure>", self._on_change)
        self.name = name

    def _on_change(self, event):
        """ abcde
        :param event:
        :type event:
        :return:
        :rtype:
        """
        self.linenumbers.redraw()
