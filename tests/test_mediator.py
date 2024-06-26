import pytest
from unittest.mock import Mock
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
        "btn_theme": mock_theme_button()
    }
    window.widgets["picklevw_tk_frame"].text = Mock()
    return window

@pytest.fixture
def mediator(mock_load_button, mock_theme_button, mock_window):
    elements = (mock_load_button, mock_theme_button, mock_window)
    return Mediator(elements)


def test_mediator_initialization(mediator, mock_load_button, mock_theme_button, mock_window):
    mock_load_button.bind.assert_called_once()
    mock_theme_button.bind.assert_called_once()
    mock_window.bind.assert_called_once()



