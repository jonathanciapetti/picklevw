"""
foobar
"""

import tkinter as tk
from src.widgets import Example, LoadButton, ThemeButton


class CustomWindow(tk.Tk):
    """
    aaa
    """
    MEDIUM_FONT = "Helvetica 12"
    BIG_FONT = "Helvetica 14"
    BIG_FONT_BOLD = "Helvetica 14 bold"
    LBL_PREFIX = "File: "
    filename = ""

    def __init__(self) -> None:
        """

        """
        super().__init__(className='picklevw')
        self.frames = {}
        self.widgets = {}
        self._pickle_str = ""

    def update_lbl_header(self, filename=''): return f'{self.LBL_PREFIX} {filename}'

    def setup_cols(self) -> None:
        """

        :return:
        :rtype:
        """
        self.grid_columnconfigure(index=0, weight=0)
        self.grid_columnconfigure(index=1, weight=1)
        self.grid_columnconfigure(index=2, weight=0)

        self.frames["btn_load_frame"].grid_columnconfigure(index=0, weight=0)
        self.frames["lbl_header_frame"].grid_columnconfigure(index=1, weight=1)
        self.frames["lbl_search_frame"].grid_columnconfigure(index=2, weight=0)
        self.frames["searchbox_frame"].grid_columnconfigure(index=3, weight=0)
        self.frames["example_frame"].grid_columnconfigure(index=0, weight=1)

    def setup_rows(self) -> None:
        """

        :return:
        :rtype:
        """
        self.grid_rowconfigure(index=0, weight=0)
        self.grid_rowconfigure(index=1, weight=1)
        self.grid_rowconfigure(index=2, weight=0)

        self.frames["example_frame"].grid_rowconfigure(index=1, weight=1)
        self.frames["lbl_footer_frame"].grid_rowconfigure(index=2, weight=1)

    def setup_frames(self) -> None:
        """

        :return:
        :rtype:
        """
        self.frames["lbl_header_frame"] = tk.Frame(self)
        self.frames["btn_load_frame"] = tk.Frame(self)
        self.frames["btn_theme_frame"] = tk.Frame(self)
        self.frames["lbl_search_frame"] = tk.Frame(self)
        self.frames["searchbox_frame"] = tk.Frame(self)
        self.frames["lbl_footer_frame"] = tk.Frame(self)
        self.frames["example_frame"] = tk.Frame(self)

        self.frames["btn_load_frame"].grid(row=0, column=0)
        self.frames["lbl_header_frame"].grid(row=0, column=1)
        self.frames["lbl_search_frame"].grid(row=0, column=2)
        self.frames["btn_theme_frame"].grid(row=0, column=3)
        self.frames["searchbox_frame"].grid(row=0, column=3)
        self.frames["example_frame"].grid(row=1, column=0, sticky="nswe", columnspan=4)
        self.frames["lbl_footer_frame"].grid(row=2, column=0, columnspan=4)

    def setup_widgets(self):
        """

        :return:
        :rtype:
        """
        # lbl_header -------------------------------------------------------------------------------
        self.widgets["lbl_header"] = tk.Label(
            master=self.frames["lbl_header_frame"],
            text=self.filename,
            font=self.MEDIUM_FONT,
            anchor="w")
        self.widgets["lbl_header"].grid(row=0, column=0, sticky='nwe', )

        # lbl_search -------------------------------------------------------------------------------
        self.widgets["lbl_search"] = tk.Label(
            master=self.frames["lbl_search_frame"],
            text="Search:",
            font=self.MEDIUM_FONT
        )
        self.widgets["lbl_search"].grid(row=0, column=2)

        # searchbox --------------------------------------------------------------------------------
        self.widgets["searchbox"] = tk.Entry(
            master=self.frames["searchbox_frame"],
            readonlybackground="white",
            font=self.MEDIUM_FONT
        )
        self.widgets["searchbox"].grid(row=0, column=3, columnspan=2)

        # example ----------------------------------------------------------------------------------
        self.widgets["example"] = Example(master=self.frames["example_frame"], name="output_box")
        self.widgets["example"].grid(row=1, column=0, sticky="nswe", columnspan=4, )

        # lbl_footer -------------------------------------------------------------------------------
        self.widgets["lbl_footer"] = tk.Label(
            master=self.frames["lbl_footer_frame"],
            text="MIT Licensed. 2024 Jonathan Ciapetti - "
                 "jonathanciapetti.it - jonathan.ciapetti@normabytes.com",
            font=self.MEDIUM_FONT,
            anchor="center")
        self.widgets["lbl_footer"].grid(row=2, column=0, columnspan=4)

        # btn_load ---------------------------------------------------------------------------------
        self.widgets["btn_load"] = LoadButton(
            master=self.frames["btn_load_frame"],
            text="Load",
            font=self.MEDIUM_FONT
        )
        self.widgets["btn_load"].grid(row=0, column=0)

        # btn_theme --------------------------------------------------------------------------------
        self.widgets["btn_theme"] = ThemeButton(
            master=self.frames["btn_load_frame"],
            text="Switch to dark mode",
            font=self.MEDIUM_FONT
        )
        self.widgets["btn_theme"].grid(row=0, column=1)

    def update_text_widget_from_queue(self, example_widget, queue):
        """Updates the text widget with messages from the queue."""
        while not queue.empty():
            message = queue.get_nowait()
            example_widget.text.delete("1.0", tk.END)
            example_widget.text.insert(tk.END, message['output'] + "\n")
            if message['status'] == 'loading':
                self.widgets['lbl_header']['text'] = 'LOADING ...'
                self.widgets['lbl_header']['bg'] = '#0000FF'
                self.widgets['lbl_header']['fg'] = '#FFFFFF'
            else:
                self.widgets['lbl_header']['bg'] = '#d9d9d9'
                self.widgets['lbl_header']['fg'] = '#000000'
                self.widgets['lbl_header']['text'] = self.update_lbl_header(message['filename'])
            # self.widgets['btn_load'].destroy()
        example_widget.text.after(
            100,
            lambda: self.update_text_widget_from_queue(
                self.widgets["example"],
                queue
            )
        )

    def ctrl_events(self, event):
        if event.state == 4 and event.keysym == 'c':
            content = self.widgets["example"].text.selection_get()
            self.clipboard_clear()
            self.clipboard_append(content)
            return "break"
        if event.state == 4 and event.keysym == 'v':
            self.widgets['example'].text.insert('end', self.selection_get(selection='CLIPBOARD'))
            return "break"
        if event.state == 4 and event.keysym == 'a':
            # select text
            self.widgets['example'].text.event_generate('<<SelectAll>>')
        return "break"
