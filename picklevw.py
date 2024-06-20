"""
foobar
"""
from __future__ import annotations

from src.custom_widgets import set_options
from src.custom_window import CustomWindow
from src.mediator import Mediator
from src.logic import output_queue, terminate_all_processes


def exit_function():
    terminate_all_processes()
    cw.destroy()


set_options()

cw = CustomWindow()
cw.setup_frames()

cw.setup_widgets()
cw.setup_rows()
cw.setup_cols()

med = Mediator([cw.widgets["btn_load"], cw.widgets["btn_theme"]], cw)
med.button_receivers = [cw.widgets["example"], ]

cw.update_text_widget_from_queue(cw.widgets["example"], output_queue)
cw.protocol('WM_DELETE_WINDOW', exit_function)

cw.mainloop()

# Setup the Tree
# tree = ttk.Treeview(example_frame, columns='Values')
# json_tree(tree, '',  ast.literal_eval(med._pickle_str) or dict())
# tree.grid()
# window.state('normal')
# window.grid_propagate(False)
