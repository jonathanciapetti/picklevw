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


def exit_function():
    """
    Function to terminate all processes and destroy the custom window.
    Called when the window is requested to close.
    """
    terminate_all_processes()
    cw.destroy()


# Set options for widgets
set_options()

# Instance of CustomWindow
cw = PicklevwTkWindow()

# Setup
cw.setup_frames()
cw.setup_widgets()
cw.setup_rows()
cw.setup_cols()

# Mediator
med = Mediator([cw.widgets["btn_load"], cw.widgets["btn_theme"]], cw)
med.button_receivers = [cw.widgets["picklevw_tk_frame"], ]

# Update the text widget
cw.loop_start_text_widget(cw.widgets["picklevw_tk_frame"], output_queue)

# Set the window protocol to call exit_function when the window is requested to close
cw.protocol('WM_DELETE_WINDOW', exit_function)

# Start the main loop of the custom window
cw.mainloop()
