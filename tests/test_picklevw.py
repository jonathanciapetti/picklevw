from unittest.mock import MagicMock, patch
import json

# Test class for PickleViewerApp
@patch("streamlit.set_page_config")
@patch("streamlit.logo")
@patch("streamlit.html")
def test_setup_page(mock_html, mock_logo, mock_config):
    from src.picklevw import PickleViewerApp

    app = PickleViewerApp()
    app.setup_page()

    mock_config.assert_called_once_with(layout="wide", page_title="picklevw", page_icon="🥒")
    mock_logo.assert_called_once()
    mock_html.assert_called_once()


@patch("streamlit.file_uploader")
def test_upload_file(mock_uploader):
    from src.picklevw import PickleViewerApp

    app = PickleViewerApp()
    app.upload_file()

    mock_uploader.assert_called_once_with(
        "Upload a Pickle (.pkl, .pickle) or Gzip-Pickle (.gz) File",
        type=["pkl", "pickle", "gz"],
        label_visibility='hidden'
    )


@patch("streamlit.warning")
@patch("streamlit.code")
@patch("streamlit.dataframe")
@patch("streamlit.markdown")
def test_display_content_json(mock_markdown, mock_dataframe, mock_code, mock_warning):
    from src.picklevw import PickleViewerApp

    app = PickleViewerApp()

    # Serializable object
    obj = {"key": "value"}
    app.display_content(obj, False, False)

    mock_markdown.assert_called_once_with("**Content**")
    mock_code.assert_called_once_with(json.dumps(obj, indent=4), language="json")
    mock_dataframe.assert_not_called()
    mock_warning.assert_not_called()


@patch("streamlit.error")
# @patch("streamlit.warning")
@patch("src.picklevw.PickleLoader")
# def test_handle_file_success(mock_loader_class, mock_error, mock_warning):
def test_handle_file_success(mock_loader_class, mock_error):
    from src.picklevw import PickleViewerApp

    app = PickleViewerApp()
    mock_loader = MagicMock()
    mock_loader.load.return_value = ({"a": 1}, False, False)
    mock_loader_class.return_value = mock_loader

    app.display_content = MagicMock()

    mock_file = MagicMock()
    app.handle_file(mock_file)

    app.display_content.assert_called_once()
    mock_error.assert_not_called()

    # mock_warning.assert_called_once_with("picklevw could not read the content of this file.")


@patch("streamlit.warning")
@patch("src.picklevw.PickleLoader")
def test_handle_file_exception(mock_loader_class, mock_warning):
    from src.picklevw import PickleViewerApp

    app = PickleViewerApp()
    mock_loader = MagicMock()
    mock_loader.load.side_effect = Exception("test error")
    mock_loader_class.return_value = mock_loader

    mock_file = MagicMock()
    app.handle_file(mock_file)

    mock_warning.assert_called_once_with("picklevw could not read the content of this file.")
