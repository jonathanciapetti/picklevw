import pytest
from unittest.mock import MagicMock, patch
from src.picklevw import PickleViewerApp
from src.picklevw import ExceptionUnsafePickle


@pytest.fixture
def app():
    return PickleViewerApp()


@patch("src.picklevw.st")
@patch("src.picklevw.cfg")
def test_setup_page(mock_cfg, mock_st, app):
    mock_cfg.UI = {
        "layout": "wide",
        "title": "Test Title",
        "icon": "🧪",
        "logo_size": "large",
        "PICKLE_DOCS_URL": "http://example.com",
    }
    mock_cfg.CONFIG = {"version": "1.0.0"}
    mock_cfg.MESSAGES = {
        "setup_page_html": "<p>{url}</p> <span>{version}</span>"
    }
    app.setup_page()
    mock_st.set_page_config.assert_called_once()
    mock_st.logo.assert_called_once()
    mock_st.html.assert_called_once()


@patch("src.picklevw.st")
@patch("src.picklevw.cfg")
def test_upload_file(mock_cfg, mock_st):
    mock_cfg.UI = {"file_extensions": [".pkl"]}
    mock_cfg.MESSAGES = {"UPLOAD_PROMPT": "Upload file"}
    PickleViewerApp.upload_file()
    mock_st.file_uploader.assert_called_once()


@patch("src.picklevw.st")
@patch("src.picklevw.PickleLoader")
def test_handle_file_success(mock_loader_class, mock_st, app):
    mock_loader = MagicMock()
    mock_loader.load.return_value = ({"a": 1}, False, True)
    mock_loader_class.return_value = mock_loader

    app.display_content = MagicMock()
    mock_file = MagicMock()
    app.handle_file(mock_file, allow_unsafe_file=False)

    app.display_content.assert_called_once()
    mock_st.error.assert_not_called()


@patch("src.picklevw.st")
def test_handle_file_unsafe_exception(mock_st, app):
    app.display_content = MagicMock()
    mock_file = MagicMock()
    with patch("src.picklevw.PickleLoader", side_effect=ExceptionUnsafePickle("unsafe")):
        app.handle_file(mock_file, allow_unsafe_file=True)
        mock_st.error.assert_called_once_with("unsafe")
        mock_st.stop.assert_called_once()


@patch("src.picklevw.st")
@patch("src.picklevw.cfg")
@patch.object(PickleViewerApp, "upload_file", return_value=None)
def test_run_with_no_file(mock_upload, mock_cfg, mock_st, app):
    mock_cfg.CONFIG = {"allow_unsafe": False, "always_disallow_unsafe": False}
    mock_cfg.MESSAGES = {
        "TOGGLER_TEXT": "Toggle",
        "TOGGLER_HELP": "Help",
        "UNSAFE_WARNING": "Warning"
    }
    app.setup_page = MagicMock()
    app.handle_file = MagicMock()

    app.run()
    app.setup_page.assert_called_once()
    mock_st.toggle.assert_called_once()
    app.handle_file.assert_not_called()


@patch("src.picklevw.st")
@patch("src.picklevw.cfg")
@patch.object(PickleViewerApp, "upload_file")
def test_run_with_file(mock_upload, mock_cfg, mock_st, app):
    mock_cfg.CONFIG = {"allow_unsafe": False, "always_disallow_unsafe": False}
    mock_cfg.MESSAGES = {
        "TOGGLER_TEXT": "Toggle",
        "TOGGLER_HELP": "Help",
        "UNSAFE_WARNING": "Warning"
    }
    app.setup_page = MagicMock()
    app.handle_file = MagicMock()
    mock_upload.return_value = MagicMock()

    app.run()
    app.setup_page.assert_called_once()
    app.handle_file.assert_called_once()
