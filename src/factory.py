"""
Module for creating and managing custom widgets in the Picklevw application.
"""

from typing import TypeAlias
from src.widgets import PicklevwTkLoadButton, PicklevwTkThemeButton, PicklevwTkFrame

WidgetType: TypeAlias = PicklevwTkLoadButton | PicklevwTkThemeButton | PicklevwTkFrame


class WidgetFactory:
    """ Factory class for creating widgets used in the Picklevw application.
    """

    @staticmethod
    def create_widget(widget_type: str, *args, **kwargs) -> WidgetType:
        """ Create and return a widget of the specified type.

        :param widget_type: The type of widget to create. Must be one of
                            'load_button', 'theme_button', or 'frame'.
        :type widget_type: str
        :param args: widget initializer args.
        :param kwargs: widget initializer kwargs.
        :return: An instance of the specified widget type.
        :rtype: WidgetType
        :raises ValueError: If the specified widget type is not recognized.
        """
        if widget_type == "load_button":
            return PicklevwTkLoadButton(*args, **kwargs)
        elif widget_type == "theme_button":
            return PicklevwTkThemeButton(*args, **kwargs)
        elif widget_type == "frame":
            return PicklevwTkFrame(*args, **kwargs)
        else:
            raise ValueError(f"Unknown widget type: {widget_type}")
