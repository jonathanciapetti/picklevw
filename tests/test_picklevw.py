import pytest
import pandas as pd
import numpy as np
from unittest.mock import MagicMock, Mock, patch
from src.picklevw import PickleViewerApp, ExceptionUnsafePickle


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


@patch('src.picklevw.st')
@patch('src.picklevw.cfg')
def test_display_content_none_object(mock_cfg, mock_st):
    """Test displaying None object when is_dataframe is False"""
    mock_cfg.MESSAGES = {
        "CONTENT_DISPLAY": "Content:",
        "GENERIC_LOAD_ERROR": "Error loading"
    }
    PickleViewerApp.display_content(None, were_spared_objs=False, is_dataframe=False)
    mock_st.markdown.assert_called_once_with("Content:")
    mock_st.warning.assert_called_once_with("Error loading")


@patch('src.picklevw.st')
@patch('src.picklevw.cfg')
def test_display_content_dataframe(mock_cfg, mock_st):
    """Test displaying a pandas DataFrame"""
    df = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})
    mock_cfg.MESSAGES = {
        "CONTENT_DISPLAY": "Content:",
        "row_col_summary": "DataFrame with {rows} rows and {cols} columns"
    }

    PickleViewerApp.display_content(df, were_spared_objs=False, is_dataframe=True)

    mock_st.markdown.assert_called_once_with("Content:")
    mock_st.write.assert_called_once_with("DataFrame with 2 rows and 2 columns")
    mock_st.dataframe.assert_called_once_with(df)


@patch('src.picklevw.st')
@patch('src.picklevw.cfg')
def test_display_content_series(mock_cfg, mock_st):
    """Test displaying a pandas Series"""
    series = pd.Series([1, 2, 3], name="test_series")
    mock_cfg.MESSAGES = {
        "CONTENT_DISPLAY": "Content:",
        "CHART": "Chart:"
    }

    PickleViewerApp.display_content(series, were_spared_objs=False, is_dataframe=False)

    mock_st.markdown.assert_any_call("Content:")
    mock_st.write.assert_called_once_with("Pandas or NumPy Series: **test_series**, 3 elements")
    mock_st.dataframe.assert_called_once()
    pd.testing.assert_frame_equal(
        mock_st.dataframe.call_args[0][0],
        series.to_frame()
    )
    mock_st.line_chart.assert_called_once_with(series)


@patch('src.picklevw.st')
@patch('src.picklevw.cfg')
def test_display_content_json_serializable(mock_cfg, mock_st):
    """Test displaying a JSON-serializable object"""
    obj = {"key": "value"}
    mock_cfg.MESSAGES = {
        "CONTENT_DISPLAY": "Content:"
    }

    PickleViewerApp.display_content(obj, were_spared_objs=False, is_dataframe=False)

    mock_st.markdown.assert_called_once_with("Content:")
    mock_st.code.assert_called_once_with('{\n    "key": "value"\n}', language="json")


@patch('src.picklevw.st')
@patch('src.picklevw.cfg')
def test_display_content_non_serializable(mock_cfg, mock_st):
    """Test displaying a non-JSON-serializable object"""

    class NonSerializable:
        pass

    obj = NonSerializable()
    mock_cfg.MESSAGES = {
        "CONTENT_DISPLAY": "Content:",
        "NOT_JSON_WARNING": "Not JSON serializable"
    }

    PickleViewerApp.display_content(obj, were_spared_objs=False, is_dataframe=False)

    mock_st.markdown.assert_called_once_with("Content:")
    mock_st.warning.assert_called_once_with("Not JSON serializable")
