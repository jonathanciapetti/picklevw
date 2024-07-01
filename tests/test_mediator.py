import pytest
from unittest.mock import Mock, patch
from src.widgets import PicklevwTkLoadButton, PicklevwTkThemeButton, PicklevwTkFrame
from src.window import PicklevwTkWindow
from src.mediator import Mediator


@pytest.fixture
def mock_load_button():
    return Mock(spec=PicklevwTkLoadButton)


@pytest.fixture
def mock_theme_button():
    return Mock(spec=PicklevwTkThemeButton)


@pytest.fixture
def mock_window(mock_theme_button):
    window = Mock(spec=PicklevwTkWindow)
    window.widgets = {
        "picklevw_tk_frame": Mock(spec=PicklevwTkFrame),
        "btn_theme": mock_theme_button(),
    }
    window.widgets["picklevw_tk_frame"].text = Mock()
    return window


@pytest.fixture
def mediator(mock_load_button, mock_theme_button, mock_window):
    return Mediator(mock_load_button, mock_theme_button, mock_window)


def test_mediator_initialization(
    mediator, mock_load_button, mock_theme_button, mock_window
):
    mock_load_button.bind.assert_called_once()
    mock_theme_button.bind.assert_called_once()
    mock_window.bind.assert_called_once()


def test_mediator_initialization_unexpected_error(
    mock_load_button, mock_theme_button, mock_window
):
    mock_window.bind.side_effect = Exception("Unexpected error")
    with patch("tkinter.messagebox.showerror") as mock_showerror:
        Mediator(mock_window, mock_load_button, mock_theme_button)
        mock_showerror.assert_called_once_with(
            title="Error", message="Unexpected error: Unexpected error"
        )
