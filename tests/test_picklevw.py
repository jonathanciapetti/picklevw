from unittest.mock import MagicMock, patch
import json
import pandas as pd


@patch("streamlit.set_page_config")
@patch("streamlit.logo")
@patch("streamlit.html")
def test_setup_page(mock_html, mock_logo, mock_config):
    from src.picklevw import PickleViewerApp

    app = PickleViewerApp()
    app.setup_page()

    mock_config.assert_called_once_with(
        layout="wide", page_title="picklevw", page_icon="🥒"
    )
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
        label_visibility="hidden",
    )


@patch("streamlit.warning")
@patch("streamlit.code")
@patch("streamlit.dataframe")
@patch("streamlit.markdown")
def test_display_content_json(mock_markdown, mock_dataframe, mock_code, mock_warning):
    from src.picklevw import PickleViewerApp

    app = PickleViewerApp()
    obj = {"key": "value"}
    app.display_content(obj, False, False)

    mock_markdown.assert_called_once_with("**Content**")
    mock_code.assert_called_once_with(json.dumps(obj, indent=4), language="json")
    mock_dataframe.assert_not_called()
    mock_warning.assert_not_called()


@patch("streamlit.warning")
@patch("streamlit.dataframe")
@patch("streamlit.markdown")
def test_display_content_dataframe(mock_markdown, mock_dataframe, mock_warning):
    from src.picklevw import PickleViewerApp

    app = PickleViewerApp()
    df = pd.DataFrame({"col1": [1, 2]})
    app.display_content(df, False, True)

    mock_markdown.assert_called_once_with("**Content**")
    mock_dataframe.assert_called_once_with(df)
    mock_warning.assert_not_called()


@patch("streamlit.warning")
@patch("streamlit.markdown")
def test_display_content_not_serializable(mock_markdown, mock_warning):
    from src.picklevw import PickleViewerApp

    class NonSerializable:
        pass

    app = PickleViewerApp()
    obj = NonSerializable()
    app.display_content(obj, False, False)

    mock_markdown.assert_called_once_with("**Content**")
    mock_warning.assert_called_once_with(
        "The object is not JSON serializable and is not a DataFrame."
    )


@patch("streamlit.error")
@patch("src.picklevw.PickleLoader")
def test_handle_file_exception_unsafe_pickle(mock_loader_class, mock_error):
    from src.picklevw import PickleViewerApp
    from src.picklevw import ExceptionUnsafePickle

    app = PickleViewerApp()
    mock_loader = MagicMock()
    mock_loader.load.side_effect = ExceptionUnsafePickle("Unsafe pickle")
    mock_loader_class.return_value = mock_loader

    app.handle_file(MagicMock())
    mock_error.assert_called_once_with("Unsafe pickle")


@patch("streamlit.warning")
@patch("src.picklevw.PickleLoader")
def test_handle_file_exception(mock_loader_class, mock_warning):
    from src.picklevw import PickleViewerApp

    app = PickleViewerApp()
    mock_loader = MagicMock()
    mock_loader.load.side_effect = Exception("test error")
    mock_loader_class.return_value = mock_loader

    app.handle_file(MagicMock())
    mock_warning.assert_called_once_with(
        "picklevw could not read the content of this file."
    )


@patch("streamlit.error")
@patch("src.picklevw.PickleLoader")
def test_handle_file_success(mock_loader_class, mock_error):
    from src.picklevw import PickleViewerApp

    app = PickleViewerApp()
    mock_loader = MagicMock()
    mock_loader.load.return_value = ({"a": 1}, False, False)
    mock_loader_class.return_value = mock_loader

    app.display_content = MagicMock()
    app.handle_file(MagicMock())

    app.display_content.assert_called_once()
    mock_error.assert_not_called()


@patch("src.picklevw.PickleViewerApp.setup_page")
@patch("src.picklevw.PickleViewerApp.upload_file")
@patch("src.picklevw.PickleViewerApp.handle_file")
def test_run_with_file(mock_handle_file, mock_upload_file, mock_setup_page):
    from src.picklevw import PickleViewerApp

    app = PickleViewerApp()
    mock_upload_file.return_value = MagicMock()
    app.run()

    mock_setup_page.assert_called_once()
    mock_upload_file.assert_called_once()
    mock_handle_file.assert_called_once()
#
