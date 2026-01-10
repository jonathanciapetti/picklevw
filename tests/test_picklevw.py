import pytest
import pandas as pd
from unittest.mock import MagicMock, Mock, patch
from src.picklevw import PickleViewerApp, ExceptionUnsafePickle
from src.handlers import (
    handle_streamlit_none,
    handle_streamlit_json,
    handle_streamlit_ndarray,
    handle_streamlit_df,
    handle_streamlit_pd_series,
)


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
def test_process_file_success(mock_loader_class, mock_st, app):
    mock_loader = MagicMock()
    mock_loader.load.return_value = ({"a": 1}, False, True)
    mock_loader_class.return_value = mock_loader

    app.display_content = MagicMock()
    mock_file = MagicMock()
    app.process_file(mock_file, allow_unsafe_file=False)

    app.display_content.assert_called_once()
    mock_st.error.assert_not_called()


@patch("src.picklevw.st")
def test_process_file_unsafe_exception(mock_st, app):
    app.display_content = MagicMock()
    mock_file = MagicMock()
    with patch("src.picklevw.PickleLoader", side_effect=ExceptionUnsafePickle("unsafe")):
        app.process_file(mock_file, allow_unsafe_file=True)
        mock_st.error.assert_called_once_with("unsafe")
        mock_st.stop.assert_called_once()


@patch("src.picklevw.st")
@patch("src.picklevw.cfg")
@patch.object(PickleViewerApp, "upload_file", return_value=None)
def test_run_with_no_file(mock_upload, mock_cfg, mock_st, app):
    mock_cfg.CONFIG = {"allow_unsafe": False, "disable_allow_unsafe": False}
    mock_cfg.MESSAGES = {
        "TOGGLER_TEXT": "Toggle",
        "TOGGLER_HELP": "Help",
        "UNSAFE_WARNING": "Warning"
    }
    app.setup_page = MagicMock()
    app.process_file = MagicMock()

    app.run()
    app.setup_page.assert_called_once()
    mock_st.toggle.assert_called_once()
    app.process_file.assert_not_called()


@patch("src.picklevw.st")
@patch("src.picklevw.cfg")
@patch.object(PickleViewerApp, "upload_file")
def test_run_with_file(mock_upload, mock_cfg, mock_st, app):
    mock_cfg.CONFIG = {"allow_unsafe": False, "disable_allow_unsafe": False}
    mock_cfg.MESSAGES = {
        "TOGGLER_TEXT": "Toggle",
        "TOGGLER_HELP": "Help",
        "UNSAFE_WARNING": "Warning"
    }
    app.setup_page = MagicMock()
    app.process_file = MagicMock()
    mock_upload.return_value = MagicMock()

    app.run()
    app.setup_page.assert_called_once()
    app.process_file.assert_called_once()


@patch('src.handlers.builtin_handlers.st')  # Fixed: patch in the handler module
@patch('src.handlers.builtin_handlers.cfg')
def test_handle_streamlit_none(mock_cfg, mock_st):
    mock_cfg.MESSAGES = {
        "GENERIC_LOAD_ERROR": "Error loading"
    }
    handle_streamlit_none()
    mock_st.warning.assert_called_once_with("Error loading")


@patch('src.handlers.pandas_handlers.pandas_dataframe_handlers.st')
@patch('src.handlers.pandas_handlers.pandas_dataframe_handlers.cfg')
def test_handle_streamlit_df(mock_cfg, mock_st):
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    mock_cfg.MESSAGES = {
        "row_col_summary": "Pandas DataFrame with **{rows}** rows and **{cols}** columns"
    }
    handle_streamlit_df(df)
    mock_st.write.assert_called_once_with("Pandas DataFrame with **2** rows and **2** columns")
    mock_st.dataframe.assert_called_once_with(df)


@patch(
    'src.handlers.pandas_handlers.pandas_series_handlers.st')  # Fixed: patch in the handler module
@patch('src.handlers.pandas_handlers.pandas_series_handlers.cfg')
def test_handle_streamlit_pd_series(mock_cfg, mock_st):
    series = pd.Series([10, 20, 30], name="my_series")
    mock_cfg.MESSAGES = {
        "CHART": "Chart:"
    }
    handle_streamlit_pd_series(series)
    mock_st.write.assert_called_once_with("Pandas Series: **my_series**, 3 elements")
    mock_st.dataframe.assert_called_once()
    pd.testing.assert_frame_equal(
        mock_st.dataframe.call_args[0][0],
        series.to_frame()
    )
    mock_st.markdown.assert_called_with("Chart:")
    mock_st.line_chart.assert_called_once_with(series)


@patch('src.handlers.builtin_handlers.st')  # Fixed: patch in the handler module
@patch('src.handlers.builtin_handlers.cfg')
def test_handle_streamlit_json(mock_cfg, mock_st):
    mock_cfg.MESSAGES = {}
    obj = {"x": 123}
    handle_streamlit_json(obj, were_spared_objs=False)
    mock_st.code.assert_called_once_with('{\n    "x": 123\n}', language="json")

    # Test also the spared format
    mock_st.reset_mock()  # Reset the mock for second test
    handle_streamlit_json({"y": "foo"}, were_spared_objs=True)
    mock_st.code.assert_called_once()


@patch('src.handlers.numpy_handlers.numpy_ndarray_handlers.st')
@patch('src.handlers.numpy_handlers.numpy_ndarray_handlers.cfg')
@patch('src.handlers.numpy_handlers.numpy_ndarray_handlers.pd')
def test_handle_streamlit_ndarray_1d_numeric(mock_pd, mock_cfg, mock_st):
    """Test handling 1D numeric numpy array"""
    import numpy as np

    mock_cfg.MESSAGES = {"CHART": "Chart:"}
    arr = np.array([1, 2, 3, 4, 5])
    mock_dataframe = MagicMock()
    mock_pd.DataFrame.return_value = mock_dataframe

    handle_streamlit_ndarray(arr)

    mock_st.write.assert_called_once_with("NumPy ndarray: shape = (5,), dtype = int64")
    mock_pd.DataFrame.assert_called_with(arr, columns=["Values"])
    mock_st.dataframe.assert_called_once_with(mock_dataframe)
    mock_st.markdown.assert_called_once_with("Chart:")
    mock_st.line_chart.assert_called_once_with(arr)


@patch('src.handlers.numpy_handlers.numpy_ndarray_handlers.st')
@patch('src.handlers.numpy_handlers.numpy_ndarray_handlers.cfg')
@patch('src.handlers.numpy_handlers.numpy_ndarray_handlers.pd')
def test_handle_streamlit_ndarray_1d_non_numeric(mock_pd, mock_cfg, mock_st):
    """Test handling 1D non-numeric numpy array"""
    import numpy as np

    mock_cfg.MESSAGES = {"CHART": "Chart:"}
    arr = np.array(['a', 'b', 'c'])
    mock_dataframe = MagicMock()
    mock_pd.DataFrame.return_value = mock_dataframe

    handle_streamlit_ndarray(arr)

    mock_st.write.assert_called_once_with("NumPy ndarray: shape = (3,), dtype = <U1")
    mock_pd.DataFrame.assert_called_with(arr, columns=["Values"])
    mock_st.dataframe.assert_called_once_with(mock_dataframe)
    # Should not show chart for non-numeric data
    mock_st.markdown.assert_not_called()
    mock_st.line_chart.assert_not_called()


@patch('src.handlers.numpy_handlers.numpy_ndarray_handlers.st')
@patch('src.handlers.numpy_handlers.numpy_ndarray_handlers.cfg')
@patch('src.handlers.numpy_handlers.numpy_ndarray_handlers.pd')
def test_handle_streamlit_ndarray_2d_numeric(mock_pd, mock_cfg, mock_st):
    """Test handling 2D numeric numpy array"""
    import numpy as np

    mock_cfg.MESSAGES = {"CHART": "Chart:"}
    arr = np.array([[1, 2, 3], [4, 5, 6]])
    mock_dataframe = MagicMock()
    mock_pd.DataFrame.return_value = mock_dataframe

    handle_streamlit_ndarray(arr)

    mock_st.write.assert_called_once_with("NumPy ndarray: shape = (2, 3), dtype = int64")
    # DataFrame called twice: once for display, once for chart
    assert mock_pd.DataFrame.call_count == 2
    mock_pd.DataFrame.assert_any_call(arr)
    mock_st.dataframe.assert_called_once_with(mock_dataframe)
    mock_st.markdown.assert_called_once_with("Chart:")
    mock_st.line_chart.assert_called_once_with(mock_dataframe)


@patch('src.handlers.numpy_handlers.numpy_ndarray_handlers.st')
@patch('src.handlers.numpy_handlers.numpy_ndarray_handlers.cfg')
@patch('src.handlers.numpy_handlers.numpy_ndarray_handlers.pd')
def test_handle_streamlit_ndarray_2d_non_numeric(mock_pd, mock_cfg, mock_st):
    """Test handling 2D non-numeric numpy array"""
    import numpy as np

    mock_cfg.MESSAGES = {"CHART": "Chart:"}
    arr = np.array([['a', 'b'], ['c', 'd']])
    mock_dataframe = MagicMock()
    mock_pd.DataFrame.return_value = mock_dataframe

    handle_streamlit_ndarray(arr)

    mock_st.write.assert_called_once_with("NumPy ndarray: shape = (2, 2), dtype = <U1")
    mock_pd.DataFrame.assert_called_once_with(arr)
    mock_st.dataframe.assert_called_once_with(mock_dataframe)
    # Should not show chart for non-numeric data
    mock_st.markdown.assert_not_called()
    mock_st.line_chart.assert_not_called()


@patch('src.handlers.numpy_handlers.numpy_ndarray_handlers.st')
@patch('src.handlers.numpy_handlers.numpy_ndarray_handlers.cfg')
def test_handle_streamlit_ndarray_3d(mock_cfg, mock_st):
    """Test handling 3D numpy array"""
    import numpy as np

    mock_cfg.MESSAGES = {"CHART": "Chart:"}
    arr = np.array([[[1, 2], [3, 4]], [[5, 6], [7, 8]]])

    handle_streamlit_ndarray(arr)

    mock_st.write.assert_called_once_with("NumPy ndarray: shape = (2, 2, 2), dtype = int64")
    mock_st.warning.assert_called_once_with(
        "NumPy array has more than 2 dimensions and cannot be displayed directly.")
    # Should not create dataframe or chart for 3D arrays
    mock_st.dataframe.assert_not_called()
    mock_st.markdown.assert_not_called()
    mock_st.line_chart.assert_not_called()


@patch('src.handlers.numpy_handlers.numpy_ndarray_handlers.st')
@patch('src.handlers.numpy_handlers.numpy_ndarray_handlers.cfg')
@patch('src.handlers.numpy_handlers.numpy_ndarray_handlers.pd')
def test_handle_streamlit_ndarray_float_type(mock_pd, mock_cfg, mock_st):
    """Test handling numpy array with float dtype"""
    import numpy as np

    mock_cfg.MESSAGES = {"CHART": "Chart:"}
    arr = np.array([1.5, 2.7, 3.1])
    mock_dataframe = MagicMock()
    mock_pd.DataFrame.return_value = mock_dataframe

    handle_streamlit_ndarray(arr)

    mock_st.write.assert_called_once_with("NumPy ndarray: shape = (3,), dtype = float64")
    mock_pd.DataFrame.assert_called_with(arr, columns=["Values"])
    mock_st.dataframe.assert_called_once_with(mock_dataframe)
    mock_st.markdown.assert_called_once_with("Chart:")
    mock_st.line_chart.assert_called_once_with(arr)


@patch('src.handlers.numpy_handlers.numpy_ndarray_handlers.st')
@patch('src.handlers.numpy_handlers.numpy_ndarray_handlers.cfg')
@patch('src.handlers.numpy_handlers.numpy_ndarray_handlers.pd')
def test_handle_streamlit_ndarray_empty_1d(mock_pd, mock_cfg, mock_st):
    """Test handling empty 1D numpy array"""
    import numpy as np

    mock_cfg.MESSAGES = {"CHART": "Chart:"}
    arr = np.array([])
    mock_dataframe = MagicMock()
    mock_pd.DataFrame.return_value = mock_dataframe

    handle_streamlit_ndarray(arr)

    mock_st.write.assert_called_once_with("NumPy ndarray: shape = (0,), dtype = float64")
    mock_pd.DataFrame.assert_called_with(arr, columns=["Values"])
    mock_st.dataframe.assert_called_once_with(mock_dataframe)
    # Should show chart even for empty numeric array
    mock_st.markdown.assert_called_once_with("Chart:")
    mock_st.line_chart.assert_called_once_with(arr)


@patch('src.handlers.numpy_handlers.numpy_ndarray_handlers.st')
@patch('src.handlers.numpy_handlers.numpy_ndarray_handlers.cfg')
@patch('src.handlers.numpy_handlers.numpy_ndarray_handlers.pd')
def test_handle_streamlit_ndarray_single_element(mock_pd, mock_cfg, mock_st):
    """Test handling single-element numpy array"""
    import numpy as np

    mock_cfg.MESSAGES = {"CHART": "Chart:"}
    arr = np.array([42])
    mock_dataframe = MagicMock()
    mock_pd.DataFrame.return_value = mock_dataframe

    handle_streamlit_ndarray(arr)

    mock_st.write.assert_called_once_with("NumPy ndarray: shape = (1,), dtype = int64")
    mock_pd.DataFrame.assert_called_with(arr, columns=["Values"])
    mock_st.dataframe.assert_called_once_with(mock_dataframe)
    mock_st.markdown.assert_called_once_with("Chart:")
    mock_st.line_chart.assert_called_once_with(arr)


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
