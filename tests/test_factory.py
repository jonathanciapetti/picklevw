import pytest
from src.widgets import PicklevwTkLoadButton, PicklevwTkThemeButton, PicklevwTkFrame
from src.factory import WidgetFactory  # Assuming you named the factory module widget_factory


def test_create_load_button():
    load_button = WidgetFactory.create_widget('load_button')
    assert isinstance(load_button, PicklevwTkLoadButton)


def test_create_theme_button():
    theme_button = WidgetFactory.create_widget('theme_button')
    assert isinstance(theme_button, PicklevwTkThemeButton)


def test_create_frame():
    frame = WidgetFactory.create_widget('frame', name='picklevw')
    assert isinstance(frame, PicklevwTkFrame)


def test_create_unknown_widget():
    with pytest.raises(ValueError) as excinfo:
        WidgetFactory.create_widget('unknown')
    assert str(excinfo.value) == "Unknown widget type: unknown"
