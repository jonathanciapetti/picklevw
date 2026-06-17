import gzip
import io
import json
import pickle
import runpy
import sys
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest

from src.picklevw import PickleViewerApp, ExceptionUnsafePickle
from src.handlers import (
    handle_streamlit_none,
    handle_streamlit_json,
    handle_streamlit_ndarray,
    handle_streamlit_df,
    handle_streamlit_pd_series,
)
from src.handlers import builtin_handlers
from src.handlers.numpy_handlers import numpy_ndarray_handlers
from src.handlers.pandas_handlers import pandas_dataframe_handlers, pandas_series_handlers


class SessionState(dict):
    """Tiny stand-in for Streamlit's session_state dict/attribute behavior."""

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError as exc:
            raise AttributeError(key) from exc

    def __setattr__(self, key, value):
        self[key] = value


@pytest.fixture
def app():
    return PickleViewerApp()


@pytest.fixture
def base_run_cfg():
    return SimpleNamespace(
        CONFIG={"allow_unsafe": False, "disable_allow_unsafe": False},
        MESSAGES={
            "TOGGLER_TEXT": "Toggle",
            "TOGGLER_HELP": "Help",
            "UNSAFE_WARNING": "Warning",
        },
    )


@pytest.fixture
def uploaded_file_factory():
    def factory(data: bytes):
        mock_file = MagicMock()
        mock_file.read.return_value = data
        mock_file.seek.return_value = None
        return mock_file

    return factory


def runtime_utils_module():
    """Return the exact utils module used by src.picklevw.

    The application imports PickleLoader with ``from utils import PickleLoader``.
    Depending on PYTHONPATH, tests may also import ``src.utils``, which creates
    a second module object. For branch tests around PickleLoader.load(), patch
    the module/globals used by the actual class under test.
    """
    import src.picklevw as picklevw_module

    return sys.modules[picklevw_module.PickleLoader.__module__]


# ---------------------------------------------------------------------------
# PickleViewerApp: GUI wrappers and page setup
# ---------------------------------------------------------------------------


def test_init_sets_base_and_logo_paths(app):
    assert app.BASE_DIR.name == "src"
    assert app.LOGO_PATH.name == "picklevw.png"
    assert app.LOGO_PATH.parent.name == "media"


@patch("src.picklevw.st")
def test_set_gui_page_config_delegates_to_streamlit(mock_st):
    PickleViewerApp.set_gui_page_config("wide", "Title", "🥒")

    mock_st.set_page_config.assert_called_once_with(
        layout="wide",
        page_title="Title",
        page_icon="🥒",
    )


@patch("src.picklevw.st")
def test_set_gui_logo_delegates_to_streamlit(mock_st):
    PickleViewerApp.set_gui_logo("logo.png", "large")

    mock_st.logo.assert_called_once_with(image="logo.png", size="large")


@patch("src.picklevw.st")
def test_set_gui_html_delegates_to_streamlit(mock_st):
    PickleViewerApp.set_gui_html("<p>Hello</p>")

    mock_st.html.assert_called_once_with(body="<p>Hello</p>")


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
    mock_cfg.MESSAGES = {"setup_page_html": "<p>{url}</p> <span>{version}</span>"}

    app.setup_page()

    mock_st.set_page_config.assert_called_once_with(
        layout="wide",
        page_title="Test Title",
        page_icon="🧪",
    )
    mock_st.logo.assert_called_once_with(image=app.LOGO_PATH, size="large")
    mock_st.html.assert_called_once_with(body="<p>http://example.com</p> <span>1.0.0</span>")


@patch("src.picklevw.st")
@patch("src.picklevw.cfg")
def test_upload_file(mock_cfg, mock_st):
    uploaded_file = MagicMock()
    mock_st.file_uploader.return_value = uploaded_file
    mock_cfg.UI = {"file_extensions": [".pkl"]}
    mock_cfg.MESSAGES = {"UPLOAD_PROMPT": "Upload file"}

    result = PickleViewerApp.upload_file()

    assert result is uploaded_file
    mock_st.file_uploader.assert_called_once_with(
        "Upload file",
        type=[".pkl"],
        label_visibility="hidden",
    )


# ---------------------------------------------------------------------------
# PickleViewerApp.display_content
# ---------------------------------------------------------------------------


@patch("src.picklevw.handle_streamlit_none")
@patch("src.picklevw.st")
@patch("src.picklevw.cfg")
def test_display_content_none_object(mock_cfg, mock_st, mock_handle_none):
    mock_cfg.MESSAGES = {"CONTENT_DISPLAY": "Content:"}

    PickleViewerApp.display_content(None, were_spared_objs=False, is_dataframe=False)

    mock_st.markdown.assert_called_once_with("Content:")
    mock_handle_none.assert_called_once_with()


@patch("src.picklevw.handle_streamlit_df")
@patch("src.picklevw.st")
@patch("src.picklevw.cfg")
def test_display_content_dataframe(mock_cfg, mock_st, mock_handle_df):
    df = pd.DataFrame({"a": [1, 2]})
    mock_cfg.MESSAGES = {"CONTENT_DISPLAY": "Content:"}

    PickleViewerApp.display_content(df, were_spared_objs=False, is_dataframe=True)

    mock_st.markdown.assert_called_once_with("Content:")
    mock_handle_df.assert_called_once_with(df)


@patch("src.picklevw.handle_streamlit_pd_series")
@patch("src.picklevw.st")
@patch("src.picklevw.cfg")
def test_display_content_series(mock_cfg, mock_st, mock_handle_series):
    series = pd.Series([1, 2, 3], name="numbers")
    mock_cfg.MESSAGES = {"CONTENT_DISPLAY": "Content:"}

    PickleViewerApp.display_content(series, were_spared_objs=False, is_dataframe=False)

    mock_st.markdown.assert_called_once_with("Content:")
    mock_handle_series.assert_called_once_with(series)


@patch("src.picklevw.handle_streamlit_ndarray")
@patch("src.picklevw.st")
@patch("src.picklevw.cfg")
def test_display_content_ndarray(mock_cfg, mock_st, mock_handle_ndarray):
    arr = np.array([1, 2, 3])
    mock_cfg.MESSAGES = {"CONTENT_DISPLAY": "Content:"}

    PickleViewerApp.display_content(arr, were_spared_objs=False, is_dataframe=False)

    mock_st.markdown.assert_called_once_with("Content:")
    mock_handle_ndarray.assert_called_once_with(arr)


@patch("src.picklevw.handle_streamlit_json")
@patch("src.picklevw.st")
@patch("src.picklevw.cfg")
def test_display_content_json_serializable(mock_cfg, mock_st, mock_handle_json):
    obj = {"x": 123}
    mock_cfg.MESSAGES = {"CONTENT_DISPLAY": "Content:"}

    PickleViewerApp.display_content(obj, were_spared_objs=True, is_dataframe=False)

    mock_st.markdown.assert_called_once_with("Content:")
    mock_handle_json.assert_called_once_with(obj, True)


@patch("src.picklevw.st")
@patch("src.picklevw.cfg")
def test_display_content_non_serializable(mock_cfg, mock_st):
    class NonSerializable:
        pass

    mock_cfg.MESSAGES = {
        "CONTENT_DISPLAY": "Content:",
        "NOT_JSON_WARNING": "Not JSON serializable",
    }

    PickleViewerApp.display_content(NonSerializable(), were_spared_objs=False, is_dataframe=False)

    mock_st.markdown.assert_called_once_with("Content:")
    mock_st.warning.assert_called_once_with("Not JSON serializable")


@patch("src.picklevw.st")
@patch("src.picklevw.cfg")
def test_display_content_reports_display_error_in_debug_mode(mock_cfg, mock_st):
    mock_cfg.MESSAGES = {"CONTENT_DISPLAY": "Content:"}
    mock_cfg.CONFIG = {"DEBUG_MODE": True}
    mock_st.markdown.side_effect = RuntimeError("boom")

    PickleViewerApp.display_content({"x": 1}, were_spared_objs=False, is_dataframe=False)

    mock_st.error.assert_called_once_with("Display Error: boom")


@patch("src.picklevw.st")
@patch("src.picklevw.cfg")
def test_display_content_suppresses_display_error_when_debug_is_disabled(mock_cfg, mock_st):
    mock_cfg.MESSAGES = {"CONTENT_DISPLAY": "Content:"}
    mock_cfg.CONFIG = {"DEBUG_MODE": False}
    mock_st.markdown.side_effect = RuntimeError("boom")

    PickleViewerApp.display_content({"x": 1}, were_spared_objs=False, is_dataframe=False)

    mock_st.error.assert_not_called()


# ---------------------------------------------------------------------------
# PickleViewerApp.process_file
# ---------------------------------------------------------------------------


@patch("src.picklevw.st")
@patch("src.picklevw.PickleLoader")
def test_process_file_success(mock_loader_class, mock_st, app):
    mock_loader = MagicMock()
    mock_loader.load.return_value = ({"a": 1}, False, True)
    mock_loader_class.return_value = mock_loader
    app.display_content = MagicMock()
    mock_file = MagicMock()

    app.process_file(mock_file, allow_unsafe_file=False)

    mock_loader_class.assert_called_once_with(mock_file, allow_unsafe_file=False)
    mock_loader.load.assert_called_once_with()
    app.display_content.assert_called_once_with({"a": 1}, False, True)
    mock_st.error.assert_not_called()


@patch("src.picklevw.st")
def test_process_file_unsafe_exception(mock_st, app):
    app.display_content = MagicMock()
    mock_file = MagicMock()

    with patch("src.picklevw.PickleLoader", side_effect=ExceptionUnsafePickle("unsafe")):
        app.process_file(mock_file, allow_unsafe_file=True)

    mock_st.error.assert_called_once_with("unsafe")
    mock_st.stop.assert_called_once_with()
    app.display_content.assert_not_called()


@pytest.mark.parametrize("exception_class", [IOError, OSError])
@patch("src.picklevw.st")
@patch("src.picklevw.cfg")
def test_process_file_access_error_in_debug_mode(mock_cfg, mock_st, exception_class, app):
    mock_cfg.CONFIG = {"DEBUG_MODE": True}

    with patch("src.picklevw.PickleLoader", side_effect=exception_class("disk nope")):
        app.process_file(MagicMock(), allow_unsafe_file=False)

    mock_st.error.assert_called_once_with("File access error: disk nope")


@patch("src.picklevw.st")
@patch("src.picklevw.cfg")
def test_process_file_access_error_is_suppressed_when_debug_is_disabled(mock_cfg, mock_st, app):
    mock_cfg.CONFIG = {"DEBUG_MODE": False}

    with patch("src.picklevw.PickleLoader", side_effect=OSError("disk nope")):
        app.process_file(MagicMock(), allow_unsafe_file=False)

    mock_st.error.assert_not_called()


@patch("src.picklevw.st")
@patch("src.picklevw.cfg")
def test_process_file_generic_error_in_debug_mode(mock_cfg, mock_st, app):
    exc = RuntimeError("bad pickle")
    mock_cfg.CONFIG = {"DEBUG_MODE": True}
    mock_cfg.MESSAGES = {"GENERIC_LOAD_ERROR": "Generic error"}

    with patch("src.picklevw.PickleLoader", side_effect=exc):
        app.process_file(MagicMock(), allow_unsafe_file=False)

    mock_st.error.assert_called_once_with("Generic error")
    mock_st.exception.assert_called_once_with(exc)


@patch("src.picklevw.st")
@patch("src.picklevw.cfg")
def test_process_file_generic_error_without_debug_trace(mock_cfg, mock_st, app):
    mock_cfg.CONFIG = {"DEBUG_MODE": False}
    mock_cfg.MESSAGES = {"GENERIC_LOAD_ERROR": "Generic error"}

    with patch("src.picklevw.PickleLoader", side_effect=RuntimeError("bad pickle")):
        app.process_file(MagicMock(), allow_unsafe_file=False)

    mock_st.error.assert_called_once_with("Generic error")
    mock_st.exception.assert_not_called()


# ---------------------------------------------------------------------------
# PickleViewerApp.run
# ---------------------------------------------------------------------------


@patch("src.picklevw.st")
@patch("src.picklevw.cfg")
@patch.object(PickleViewerApp, "upload_file", return_value=None)
def test_run_with_no_file(mock_upload, mock_cfg, mock_st, app, base_run_cfg):
    mock_cfg.CONFIG = base_run_cfg.CONFIG
    mock_cfg.MESSAGES = base_run_cfg.MESSAGES
    mock_st.session_state = SessionState()
    mock_st.toggle.return_value = False
    app.setup_page = MagicMock()
    app.process_file = MagicMock()

    app.run()

    assert mock_st.session_state.allow_unsafe_file is False
    app.setup_page.assert_called_once_with()
    mock_st.toggle.assert_called_once_with(
        "Toggle",
        key="allow_unsafe_file",
        help="Help",
        disabled=False,
    )
    mock_upload.assert_called_once_with()
    app.process_file.assert_not_called()
    mock_st.warning.assert_not_called()


@patch("src.picklevw.st")
@patch("src.picklevw.cfg")
@patch.object(PickleViewerApp, "upload_file")
def test_run_with_file(mock_upload, mock_cfg, mock_st, app, base_run_cfg):
    uploaded_file = MagicMock()
    mock_upload.return_value = uploaded_file
    mock_cfg.CONFIG = base_run_cfg.CONFIG
    mock_cfg.MESSAGES = base_run_cfg.MESSAGES
    mock_st.session_state = SessionState()
    mock_st.toggle.return_value = False
    app.setup_page = MagicMock()
    app.process_file = MagicMock()

    app.run()

    app.setup_page.assert_called_once_with()
    app.process_file.assert_called_once_with(uploaded_file, False)


@patch("src.picklevw.st")
@patch("src.picklevw.cfg")
@patch.object(PickleViewerApp, "upload_file")
def test_run_with_unsafe_toggle_warns_and_processes_with_unsafe_flag(
    mock_upload,
    mock_cfg,
    mock_st,
    app,
    base_run_cfg,
):
    uploaded_file = MagicMock()
    mock_upload.return_value = uploaded_file
    mock_cfg.CONFIG = base_run_cfg.CONFIG
    mock_cfg.MESSAGES = base_run_cfg.MESSAGES
    mock_st.session_state = SessionState({"allow_unsafe_file": False})
    mock_st.toggle.return_value = True
    app.setup_page = MagicMock()
    app.process_file = MagicMock()

    app.run()

    mock_st.warning.assert_called_once_with("Warning")
    app.process_file.assert_called_once_with(uploaded_file, True)


@patch("src.picklevw.st")
@patch("src.picklevw.cfg")
@patch.object(PickleViewerApp, "upload_file", return_value=None)
def test_run_keeps_existing_session_state_value(mock_upload, mock_cfg, mock_st, app, base_run_cfg):
    mock_cfg.CONFIG = {**base_run_cfg.CONFIG, "allow_unsafe": False}
    mock_cfg.MESSAGES = base_run_cfg.MESSAGES
    mock_st.session_state = SessionState({"allow_unsafe_file": True})
    mock_st.toggle.return_value = False
    app.setup_page = MagicMock()

    app.run()

    assert mock_st.session_state.allow_unsafe_file is True


# ---------------------------------------------------------------------------
# Streamlit handlers
# ---------------------------------------------------------------------------


@patch("src.handlers.builtin_handlers.st")
@patch("src.handlers.builtin_handlers.cfg")
def test_handle_streamlit_none(mock_cfg, mock_st):
    mock_cfg.MESSAGES = {"GENERIC_LOAD_ERROR": "Error loading"}

    handle_streamlit_none()

    mock_st.warning.assert_called_once_with("Error loading")


@patch("src.handlers.pandas_handlers.pandas_dataframe_handlers.st")
@patch("src.handlers.pandas_handlers.pandas_dataframe_handlers.cfg")
def test_handle_streamlit_df(mock_cfg, mock_st):
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    mock_cfg.MESSAGES = {
        "row_col_summary": "Pandas DataFrame with **{rows}** rows and **{cols}** columns"
    }

    handle_streamlit_df(df)

    mock_st.write.assert_called_once_with("Pandas DataFrame with **2** rows and **2** columns")
    mock_st.dataframe.assert_called_once_with(df)


@patch("src.handlers.pandas_handlers.pandas_series_handlers.st")
@patch("src.handlers.pandas_handlers.pandas_series_handlers.cfg")
def test_handle_streamlit_pd_series(mock_cfg, mock_st):
    series = pd.Series([10, 20, 30], name="my_series")
    mock_cfg.MESSAGES = {"CHART": "Chart:"}

    handle_streamlit_pd_series(series)

    mock_st.write.assert_called_once_with("Pandas Series: **my_series**, 3 elements")
    mock_st.dataframe.assert_called_once()
    pd.testing.assert_frame_equal(mock_st.dataframe.call_args[0][0], series.to_frame())
    mock_st.markdown.assert_called_with("Chart:")
    mock_st.line_chart.assert_called_once_with(series)


@patch("src.handlers.builtin_handlers.st")
@patch("src.handlers.builtin_handlers.cfg")
def test_handle_streamlit_json(mock_cfg, mock_st):
    mock_cfg.MESSAGES = {}

    handle_streamlit_json({"x": 123}, were_spared_objs=False)

    mock_st.code.assert_called_once_with('{\n    \"x\": 123\n}', language="json")


@patch("src.handlers.builtin_handlers.st")
@patch("src.handlers.builtin_handlers.cfg")
def test_handle_streamlit_json_unquotes_spared_string(mock_cfg, mock_st):
    mock_cfg.MESSAGES = {}

    builtin_handlers.handle_streamlit_json("plain string", were_spared_objs=True)

    mock_st.code.assert_called_once_with("plain string", language="json")


@patch("src.handlers.numpy_handlers.numpy_ndarray_handlers.st")
@patch("src.handlers.numpy_handlers.numpy_ndarray_handlers.cfg")
@patch("src.handlers.numpy_handlers.numpy_ndarray_handlers.pd")
def test_handle_streamlit_ndarray_1d_numeric(mock_pd, mock_cfg, mock_st):
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


@patch("src.handlers.numpy_handlers.numpy_ndarray_handlers.st")
@patch("src.handlers.numpy_handlers.numpy_ndarray_handlers.cfg")
@patch("src.handlers.numpy_handlers.numpy_ndarray_handlers.pd")
def test_handle_streamlit_ndarray_1d_non_numeric(mock_pd, mock_cfg, mock_st):
    mock_cfg.MESSAGES = {"CHART": "Chart:"}
    arr = np.array(["a", "b", "c"])
    mock_dataframe = MagicMock()
    mock_pd.DataFrame.return_value = mock_dataframe

    handle_streamlit_ndarray(arr)

    mock_st.write.assert_called_once_with("NumPy ndarray: shape = (3,), dtype = <U1")
    mock_pd.DataFrame.assert_called_with(arr, columns=["Values"])
    mock_st.dataframe.assert_called_once_with(mock_dataframe)
    mock_st.markdown.assert_not_called()
    mock_st.line_chart.assert_not_called()


@patch("src.handlers.numpy_handlers.numpy_ndarray_handlers.st")
@patch("src.handlers.numpy_handlers.numpy_ndarray_handlers.cfg")
@patch("src.handlers.numpy_handlers.numpy_ndarray_handlers.pd")
def test_handle_streamlit_ndarray_2d_numeric(mock_pd, mock_cfg, mock_st):
    mock_cfg.MESSAGES = {"CHART": "Chart:"}
    arr = np.array([[1, 2, 3], [4, 5, 6]])
    display_dataframe = MagicMock(name="display_dataframe")
    chart_dataframe = MagicMock(name="chart_dataframe")
    mock_pd.DataFrame.side_effect = [display_dataframe, chart_dataframe]

    handle_streamlit_ndarray(arr)

    mock_st.write.assert_called_once_with("NumPy ndarray: shape = (2, 3), dtype = int64")
    assert mock_pd.DataFrame.call_count == 2
    mock_pd.DataFrame.assert_any_call(arr)
    mock_st.dataframe.assert_called_once_with(display_dataframe)
    mock_st.markdown.assert_called_once_with("Chart:")
    mock_st.line_chart.assert_called_once_with(chart_dataframe)


@patch("src.handlers.numpy_handlers.numpy_ndarray_handlers.st")
@patch("src.handlers.numpy_handlers.numpy_ndarray_handlers.cfg")
@patch("src.handlers.numpy_handlers.numpy_ndarray_handlers.pd")
def test_handle_streamlit_ndarray_2d_non_numeric(mock_pd, mock_cfg, mock_st):
    mock_cfg.MESSAGES = {"CHART": "Chart:"}
    arr = np.array([["a", "b"], ["c", "d"]])
    mock_dataframe = MagicMock()
    mock_pd.DataFrame.return_value = mock_dataframe

    handle_streamlit_ndarray(arr)

    mock_st.write.assert_called_once_with("NumPy ndarray: shape = (2, 2), dtype = <U1")
    mock_pd.DataFrame.assert_called_once_with(arr)
    mock_st.dataframe.assert_called_once_with(mock_dataframe)
    mock_st.markdown.assert_not_called()
    mock_st.line_chart.assert_not_called()


@patch("src.handlers.numpy_handlers.numpy_ndarray_handlers.st")
@patch("src.handlers.numpy_handlers.numpy_ndarray_handlers.cfg")
def test_handle_streamlit_ndarray_3d(mock_cfg, mock_st):
    mock_cfg.MESSAGES = {"CHART": "Chart:"}
    arr = np.array([[[1, 2], [3, 4]], [[5, 6], [7, 8]]])

    handle_streamlit_ndarray(arr)

    mock_st.write.assert_called_once_with("NumPy ndarray: shape = (2, 2, 2), dtype = int64")
    mock_st.warning.assert_called_once_with(
        "NumPy array has more than 2 dimensions and cannot be displayed directly."
    )
    mock_st.dataframe.assert_not_called()
    mock_st.markdown.assert_not_called()
    mock_st.line_chart.assert_not_called()


@pytest.mark.parametrize(
    "arr, expected_dtype",
    [
        (np.array([1.5, 2.7, 3.1]), "float64"),
        (np.array([]), "float64"),
        (np.array([42]), "int64"),
    ],
)
@patch("src.handlers.numpy_handlers.numpy_ndarray_handlers.st")
@patch("src.handlers.numpy_handlers.numpy_ndarray_handlers.cfg")
@patch("src.handlers.numpy_handlers.numpy_ndarray_handlers.pd")
def test_handle_streamlit_ndarray_1d_numeric_edge_cases(
    mock_pd,
    mock_cfg,
    mock_st,
    arr,
    expected_dtype,
):
    mock_cfg.MESSAGES = {"CHART": "Chart:"}
    mock_dataframe = MagicMock()
    mock_pd.DataFrame.return_value = mock_dataframe

    handle_streamlit_ndarray(arr)

    mock_st.write.assert_called_once_with(
        f"NumPy ndarray: shape = {arr.shape}, dtype = {expected_dtype}"
    )
    mock_pd.DataFrame.assert_called_with(arr, columns=["Values"])
    mock_st.dataframe.assert_called_once_with(mock_dataframe)
    mock_st.markdown.assert_called_once_with("Chart:")
    mock_st.line_chart.assert_called_once_with(arr)


# ---------------------------------------------------------------------------
# utils.py coverage: security checker, reader, loader, JSON predicate
# ---------------------------------------------------------------------------


def pickle_bytes(*objects):
    return b"".join(pickle.dumps(obj) for obj in objects)


def test_pickle_security_checker_allows_severity_at_threshold(monkeypatch):
    import src.utils as utils

    fake_pickled = object()
    monkeypatch.setattr(utils.Pickled, "load", MagicMock(return_value=fake_pickled))
    monkeypatch.setattr(
        utils,
        "check_safety",
        MagicMock(return_value=SimpleNamespace(severity=SimpleNamespace(value=(1,)))),
    )
    monkeypatch.setattr(utils.cfg, "CONFIG", {"SEVERITY_THRESHOLD": 1})
    buffer = io.BytesIO(b"pickle")

    utils.PickleSecurityChecker(buffer).ensure_safe()

    utils.Pickled.load.assert_called_once_with(buffer)
    utils.check_safety.assert_called_once_with(fake_pickled)


def test_pickle_security_checker_rejects_severity_above_threshold(monkeypatch):
    import src.utils as utils
    from fickling.exception import UnsafeFileError

    monkeypatch.setattr(utils.Pickled, "load", MagicMock(return_value=object()))
    monkeypatch.setattr(
        utils,
        "check_safety",
        MagicMock(return_value=SimpleNamespace(severity=SimpleNamespace(value=(2,)))),
    )
    monkeypatch.setattr(utils.cfg, "CONFIG", {"SEVERITY_THRESHOLD": 1})

    with pytest.raises(UnsafeFileError):
        utils.PickleSecurityChecker(io.BytesIO(b"pickle")).ensure_safe()


@pytest.mark.parametrize("obj", [pd.DataFrame({"a": [1]}), pd.Series([1, 2], name="s")])
def test_pickle_reader_try_read_dataframe_returns_pandas_objects(obj):
    import src.utils as utils

    result = utils.PickleReader(io.BytesIO(pickle.dumps(obj))).try_read_dataframe()

    if isinstance(obj, pd.DataFrame):
        pd.testing.assert_frame_equal(result, obj)
    else:
        pd.testing.assert_series_equal(result, obj)


@pytest.mark.parametrize("data", [pickle.dumps({"not": "pandas"}), b"not a pickle"])
def test_pickle_reader_try_read_dataframe_returns_none_for_invalid_or_non_pandas(data):
    import src.utils as utils

    assert utils.PickleReader(io.BytesIO(data)).try_read_dataframe() is None


@pytest.mark.parametrize(
    "obj",
    [
        np.array([1, 2, 3]),
        pd.DataFrame({"a": [1]}),
        pd.Series([1, 2], name="s"),
        {"data": np.array([1, 2, 3]), "labels": [0, 1, 0]},
    ],
)
def test_pickle_reader_try_read_array_returns_supported_objects(obj):
    import src.utils as utils

    result = utils.PickleReader(io.BytesIO(pickle.dumps(obj))).try_read_array()

    if isinstance(obj, pd.DataFrame):
        pd.testing.assert_frame_equal(result, obj)
    elif isinstance(obj, pd.Series):
        pd.testing.assert_series_equal(result, obj)
    elif isinstance(obj, np.ndarray):
        np.testing.assert_array_equal(result, obj)
    else:
        assert result is obj or result.keys() == obj.keys()
        np.testing.assert_array_equal(result["data"], obj["data"])


@pytest.mark.parametrize("data", [pickle.dumps({"data": [1, 2, 3]}), pickle.dumps(123), b"bad"])
def test_pickle_reader_try_read_array_returns_none_for_unsupported_or_invalid_data(data):
    import src.utils as utils

    assert utils.PickleReader(io.BytesIO(data)).try_read_array() is None


def test_pickle_reader_try_read_objects_returns_single_object():
    import src.utils as utils

    obj, multiple = utils.PickleReader(io.BytesIO(pickle.dumps({"a": 1}))).try_read_objects()

    assert obj == {"a": 1}
    assert multiple is False


def test_pickle_reader_try_read_objects_returns_joined_string_for_multiple_objects():
    import src.utils as utils

    obj, multiple = utils.PickleReader(io.BytesIO(pickle_bytes("first", 2))).try_read_objects()

    assert obj == "first, 2"
    assert multiple is True


@pytest.mark.parametrize("data", [b"", b"not a pickle"])
def test_pickle_reader_try_read_objects_returns_none_for_empty_or_unpicklable_data(data):
    import src.utils as utils

    obj, multiple = utils.PickleReader(io.BytesIO(data)).try_read_objects()

    assert obj is None
    assert multiple is False


def test_pickle_reader_try_read_objects_swallows_unexpected_exceptions():
    import src.utils as utils

    class ExplodingBuffer(io.BytesIO):
        def read(self, *args, **kwargs):
            raise RuntimeError("boom")

    obj, multiple = utils.PickleReader(ExplodingBuffer(b"x")).try_read_objects()

    assert obj is None
    assert multiple is False


def test_pickle_loader_reads_raw_file(uploaded_file_factory):
    import src.utils as utils

    raw_data = pickle.dumps({"a": 1})
    uploaded_file = uploaded_file_factory(raw_data)

    loader = utils.PickleLoader(uploaded_file)

    uploaded_file.seek.assert_called_once_with(0)
    uploaded_file.read.assert_called_once_with()
    assert loader.raw_data == raw_data
    assert loader.is_gzipped is False
    assert loader.buffer.getvalue() == raw_data


def test_pickle_loader_decompresses_gzip(uploaded_file_factory):
    import src.utils as utils

    raw_data = pickle.dumps({"a": 1})
    uploaded_file = uploaded_file_factory(gzip.compress(raw_data))

    loader = utils.PickleLoader(uploaded_file)

    assert loader.is_gzipped is True
    assert loader.buffer.getvalue() == raw_data


def test_pickle_loader_safe_load_returns_generic_objects(monkeypatch, uploaded_file_factory):
    import src.utils as utils

    raw_data = pickle_bytes("first", 2)
    monkeypatch.setattr(utils.PickleSecurityChecker, "ensure_safe", MagicMock(return_value=None))

    obj, multiple, is_dataframe = utils.PickleLoader(uploaded_file_factory(raw_data)).load()

    assert obj == "first, 2"
    assert multiple is True
    assert is_dataframe is False


def test_pickle_loader_unsafe_allowed_returns_dataframe(monkeypatch, uploaded_file_factory):
    import src.utils as utils
    from fickling.exception import UnsafeFileError

    df = pd.DataFrame({"a": [1, 2]})
    monkeypatch.setattr(
        utils.PickleSecurityChecker,
        "ensure_safe",
        MagicMock(side_effect=UnsafeFileError(info="unsafe", filepath="file.pkl")),
    )

    obj, multiple, is_dataframe = utils.PickleLoader(
        uploaded_file_factory(pickle.dumps(df)),
        allow_unsafe_file=True,
    ).load()

    pd.testing.assert_frame_equal(obj, df)
    assert multiple is False
    assert is_dataframe is True


# def test_pickle_loader_unsafe_allowed_returns_numpy_array(monkeypatch, uploaded_file_factory):
#     import src.picklevw as picklevw_module
#
#     arr = np.array([1, 2, 3])
#
#     class FakeUnsafeFileError(Exception):
#         pass
#
#     class AlwaysUnsafeSecurityChecker:
#         def __init__(self, buffer):
#             self.buffer = buffer
#
#         def ensure_safe(self):
#             raise FakeUnsafeFileError("unsafe")
#
#     class ReaderReturningArray:
#         def __init__(self, buffer):
#             self.buffer = buffer
#
#         def try_read_dataframe(self):
#             return None
#
#         def try_read_array(self):
#             return arr
#
#         def try_read_objects(self):
#             pytest.fail("The unsafe branch should not call try_read_objects().")
#
#     loader = picklevw_module.PickleLoader(
#         uploaded_file_factory(pickle.dumps({"reader": "methods are mocked"})),
#         allow_unsafe_file=True,
#     )
#     load_globals = loader.load.__func__.__globals__
#     monkeypatch.setitem(load_globals, "UnsafeFileError", FakeUnsafeFileError)
#     monkeypatch.setitem(load_globals, "PickleSecurityChecker", AlwaysUnsafeSecurityChecker)
#     monkeypatch.setitem(load_globals, "PickleReader", ReaderReturningArray)
#
#     obj, multiple, is_dataframe = loader.load()
#
#     np.testing.assert_array_equal(obj, arr)
#     assert multiple is False
#     assert is_dataframe is True

def test_pickle_loader_unsafe_disallowed_raises_project_exception(monkeypatch, uploaded_file_factory):
    import src.utils as utils
    from fickling.exception import UnsafeFileError

    monkeypatch.setattr(
        utils.PickleSecurityChecker,
        "ensure_safe",
        MagicMock(side_effect=UnsafeFileError(info="unsafe", filepath="file.pkl")),
    )
    monkeypatch.setattr(utils.cfg, "MESSAGES", {"POTENTIAL_THREAT": "threat detected"})

    with pytest.raises(utils.ExceptionUnsafePickle, match="threat detected"):
        utils.PickleLoader(uploaded_file_factory(pickle.dumps({"a": 1}))).load()


# def test_pickle_loader_unsafe_allowed_unsupported_object_raises_project_exception(
#     monkeypatch,
#     uploaded_file_factory,
# ):
#     import src.picklevw as picklevw_module
#
#     class FakeUnsafeFileError(Exception):
#         pass
#
#     class AlwaysUnsafeSecurityChecker:
#         def __init__(self, buffer):
#             self.buffer = buffer
#
#         def ensure_safe(self):
#             raise FakeUnsafeFileError("unsafe")
#
#     class ReaderReturningNothing:
#         def __init__(self, buffer):
#             self.buffer = buffer
#
#         def try_read_dataframe(self):
#             return None
#
#         def try_read_array(self):
#             return None
#
#         def try_read_objects(self):
#             pytest.fail("The unsafe fallback should not call try_read_objects().")
#
#         def t(self):
#             return None
#
#     loader = picklevw_module.PickleLoader(
#         uploaded_file_factory(pickle.dumps({"reader": "methods are mocked"})),
#         allow_unsafe_file=True,
#     )
#     load_globals = loader.load.__func__.__globals__
#     monkeypatch.setitem(load_globals, "UnsafeFileError", FakeUnsafeFileError)
#     monkeypatch.setitem(load_globals, "PickleSecurityChecker", AlwaysUnsafeSecurityChecker)
#     monkeypatch.setitem(load_globals, "PickleReader", ReaderReturningNothing)
#     monkeypatch.setitem(load_globals["cfg"].MESSAGES, "POTENTIAL_THREAT", "threat detected")
#
#     expected_exception = load_globals["ExceptionUnsafePickle"]
#
#     with pytest.raises(expected_exception, match="threat detected"):
#         loader.load()

def test_is_json_serializable_true_and_false_cases():
    import src.utils as utils

    assert utils.is_json_serializable({"key": "value"}) is True
    assert utils.is_json_serializable([1, 2, 3]) is True
    assert utils.is_json_serializable({1, 2, 3}) is False


def test_is_json_serializable_handles_overflow_error(monkeypatch):
    import src.utils as utils

    monkeypatch.setattr(utils.json, "dumps", MagicMock(side_effect=OverflowError))

    assert utils.is_json_serializable(object()) is False


# ---------------------------------------------------------------------------
# __main__ block
# ---------------------------------------------------------------------------


def test_main_block_runs_app_without_sentry_when_debug_is_disabled(monkeypatch):
    import config
    import streamlit as streamlit_module

    fake_sentry = SimpleNamespace(init=MagicMock())
    monkeypatch.setitem(sys.modules, "sentry_sdk", fake_sentry)
    monkeypatch.setitem(config.CONFIG, "DEBUG_MODE", False)
    monkeypatch.setitem(config.CONFIG, "disable_allow_unsafe", False)
    monkeypatch.setattr(streamlit_module, "session_state", SessionState(), raising=False)
    monkeypatch.setattr(streamlit_module, "toggle", MagicMock(return_value=False), raising=False)
    monkeypatch.setattr(streamlit_module, "file_uploader", MagicMock(return_value=None), raising=False)
    monkeypatch.setattr(streamlit_module, "set_page_config", MagicMock(), raising=False)
    monkeypatch.setattr(streamlit_module, "logo", MagicMock(), raising=False)
    monkeypatch.setattr(streamlit_module, "html", MagicMock(), raising=False)
    monkeypatch.setattr(streamlit_module, "warning", MagicMock(), raising=False)

    runpy.run_path(str(sys.modules["src.picklevw"].__file__), run_name="__main__")

    fake_sentry.init.assert_not_called()
    streamlit_module.set_page_config.assert_called_once()


def test_main_block_initializes_sentry_when_debug_is_enabled(monkeypatch):
    import config
    import streamlit as streamlit_module

    fake_sentry = SimpleNamespace(init=MagicMock())
    monkeypatch.setitem(sys.modules, "sentry_sdk", fake_sentry)
    monkeypatch.setitem(config.CONFIG, "DEBUG_MODE", True)
    monkeypatch.setitem(config.CONFIG, "disable_allow_unsafe", False)
    monkeypatch.setattr(streamlit_module, "session_state", SessionState(), raising=False)
    monkeypatch.setattr(streamlit_module, "toggle", MagicMock(return_value=False), raising=False)
    monkeypatch.setattr(streamlit_module, "file_uploader", MagicMock(return_value=None), raising=False)
    monkeypatch.setattr(streamlit_module, "set_page_config", MagicMock(), raising=False)
    monkeypatch.setattr(streamlit_module, "logo", MagicMock(), raising=False)
    monkeypatch.setattr(streamlit_module, "html", MagicMock(), raising=False)
    monkeypatch.setattr(streamlit_module, "warning", MagicMock(), raising=False)

    runpy.run_path(str(sys.modules["src.picklevw"].__file__), run_name="__main__")

    fake_sentry.init.assert_called_once_with(
        dsn="https://56058342450243edb54846f5e07f2236@errors.hypatialabs.it/6",
        traces_sample_rate=1.0,
    )
    streamlit_module.set_page_config.assert_called_once()
