from src.widgets import PicklevwTkLoadButton, PicklevwTkThemeButton, PicklevwTkFrame


class WidgetFactory:
    @staticmethod
    def create_widget(widget_type, *args, **kwargs):
        if widget_type == 'load_button':
            return PicklevwTkLoadButton(*args, **kwargs)
        elif widget_type == 'theme_button':
            return PicklevwTkThemeButton(*args, **kwargs)
        elif widget_type == 'frame':
            return PicklevwTkFrame(*args, **kwargs)
        else:
            raise ValueError(f"Unknown widget type: {widget_type}")
