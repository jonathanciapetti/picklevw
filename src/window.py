"""
This module implements a custom Tkinter window for displaying
and managing widgets in a GUI application.
"""

import tkinter as tk

from src.widgets import PicklevwTkFrame, PicklevwTkLoadButton, PicklevwTkThemeButton


class PicklevwTkWindow(tk.Tk):
    """ A custom Tkinter window for displaying and managing widgets in a GUI application.
    """

    MEDIUM_FONT, BIG_FONT, BIG_FONT_BOLD = ("Helvetica 12", "Helvetica 14", "Helvetica 14 bold")
    LBL_PREFIX = "File: "
    filename = ""

    FOOTER_TEXT = ("MIT Licensed. 2024 Jonathan Ciapetti - "
                   "https://github.com/jonathanciapetti/picklevw - "
                   "jonathan.ciapetti@normabytes.com")

    def __init__(self) -> None:
        super().__init__(className='picklevw')  # This sets the title of the window.
        self.frames = {}
        self.widgets = {}
        self._pickle_str = ""

    def update_lbl_header(self, filename='') -> str:
        """ Updates the label header with the provided filename.
        :return: label header with the provided filename
        :rtype: str
        """
        return f'{self.LBL_PREFIX} {filename}'

    def setup_cols(self) -> None:
        """ Configures the grid columns for the main window and its frames. """
        self.grid_columnconfigure(index=0, weight=0)
        self.grid_columnconfigure(index=1, weight=1)
        self.grid_columnconfigure(index=2, weight=0)

        self.frames["btn_load_frame"].grid_columnconfigure(index=0, weight=0)
        self.frames["lbl_header_frame"].grid_columnconfigure(index=1, weight=1)
        self.frames["lbl_search_frame"].grid_columnconfigure(index=2, weight=0)
        self.frames["searchbox_frame"].grid_columnconfigure(index=3, weight=0)
        self.frames["example_frame"].grid_columnconfigure(index=0, weight=1)

    def setup_rows(self) -> None:
        """ Configures the grid rows for the main window and its frames. """
        self.grid_rowconfigure(index=0, weight=0)
        self.grid_rowconfigure(index=1, weight=1)
        self.grid_rowconfigure(index=2, weight=0)

        self.frames["example_frame"].grid_rowconfigure(index=1, weight=1)
        self.frames["lbl_footer_frame"].grid_rowconfigure(index=2, weight=1)

    def setup_frames(self) -> None:
        """ Initializes and places the frames within the main window. """
        for elem_name in (
                "lbl_header_frame", "btn_load_frame", "btn_theme_frame", "lbl_search_frame",
                "searchbox_frame", "lbl_footer_frame", "example_frame",
        ):
            self.frames[elem_name] = tk.Frame(self)

        self.frames["btn_load_frame"].grid(row=0, column=0)
        self.frames["lbl_header_frame"].grid(row=0, column=1)
        self.frames["lbl_search_frame"].grid(row=0, column=2)
        self.frames["btn_theme_frame"].grid(row=0, column=3)
        self.frames["searchbox_frame"].grid(row=0, column=3)
        self.frames["example_frame"].grid(row=1, column=0, sticky="nswe", columnspan=4)
        self.frames["lbl_footer_frame"].grid(row=2, column=0, columnspan=4)

    def setup_widgets(self) -> None:
        """ Initializes and places the widgets within the frames. """
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
        self.widgets["picklevw_tk_frame"] = PicklevwTkFrame(
            master=self.frames["example_frame"],
            name="output_box"
        )
        self.widgets["picklevw_tk_frame"].grid(row=1, column=0, sticky="nswe", columnspan=4)

        # lbl_footer -------------------------------------------------------------------------------
        self.widgets["lbl_footer"] = tk.Label(
            master=self.frames["lbl_footer_frame"],
            text=self.FOOTER_TEXT,
            font=self.MEDIUM_FONT,
            anchor="center")
        self.widgets["lbl_footer"].grid(row=2, column=0, columnspan=4)

        # btn_load ---------------------------------------------------------------------------------
        self.widgets["btn_load"] = PicklevwTkLoadButton(
            master=self.frames["btn_load_frame"],
            font=self.MEDIUM_FONT
        )
        self.widgets["btn_load"].grid(row=0, column=0)

        # btn_theme --------------------------------------------------------------------------------
        self.widgets["btn_theme"] = PicklevwTkThemeButton(
            master=self.frames["btn_load_frame"],
            font=self.MEDIUM_FONT
        )
        self.widgets["btn_theme"].grid(row=0, column=1)

    def loop_start_text_widget(self, example_widget, queue) -> None:
        """ Updates the text widget with messages from the queue. """
        while not queue.empty():
            message = queue.get_nowait()
            example_widget.text.delete("1.0", tk.END)
            example_widget.text.insert(tk.END, message['output'] + "\n")
            if 'messagebox' in message.keys():
                tk.messagebox.showinfo(title="Error", message=message['messagebox'])
            if message['status'] == 'loading':
                self.widgets['lbl_header']['text'] = 'LOADING ...'
                self.widgets['lbl_header']['bg'] = '#0000FF'
                self.widgets['lbl_header']['fg'] = '#FFFFFF'
            else:
                self.widgets['lbl_header']['bg'] = '#d9d9d9'
                self.widgets['lbl_header']['fg'] = '#000000'
                self.widgets['lbl_header']['text'] = self.update_lbl_header(message['filename'])
        # Important !!! Recursion:
        example_widget.text.after(
            100,
            lambda: self.loop_start_text_widget(
                self.widgets["picklevw_tk_frame"],
                queue
            )
        )

    def ctrl_events(self, event) -> str:
        """ Handles control events for copy, paste, and select-all actions.
        :return:
        :rtype: str
        """
        if event.state == 4:

            # Select text:
            if event.keysym == 'a':
                self.widgets["picklevw_tk_frame"].text.event_generate("<<SelectAll>>")

            # Copy text
            elif event.keysym == 'c':
                content = self.widgets["picklevw_tk_frame"].text.selection_get()
                self.clipboard_clear()
                self.clipboard_append(content)

            # Paste text (why, if this code is enabled, does double stuff get pasted?)
            # if event.keysym == 'v':
            #     self.widgets["picklevw_tk_frame"].text.insert(
            #         'end',
            #         self.selection_get(selection="CLIPBOARD")
            #     )

        return "break"
