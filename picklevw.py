"""
This module initializes, runs and destroy a window object.
It also ensures thread safety.
"""

from __future__ import annotations

import ctypes

from src.widgets import set_options
from src.window import PicklevwTkWindow
from src.mediator import Mediator
from src.logic import output_queue, terminate_all_processes

# Initialize X11 threads for thread safety in GUI applications
ctypes.CDLL('libX11.so.6').XInitThreads()

# Set options for widgets
set_options()

# Instance of PicklevwTkWindow
pw = PicklevwTkWindow()


def exit_function():
    """
    Function to terminate all processes and destroy the custom window.
    Called when the window is requested to close.
    """
    terminate_all_processes()
    pw.destroy()


# Setup
pw.setup_frames()
pw.setup_widgets()
pw.setup_rows()
pw.setup_cols()

# Mediator
med = Mediator([pw.widgets["btn_load"], pw.widgets["btn_theme"]], pw)

# Update the text widget
pw.loop_start_text_widget(pw.widgets["picklevw_tk_frame"], output_queue)

# Set the window protocol to call exit_function when the window is requested to close
pw.protocol('WM_DELETE_WINDOW', exit_function)

# Start the main loop of the custom window
pw.mainloop()
