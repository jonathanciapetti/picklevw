from pathlib import Path

import numpy as np
import pandas as pd

import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile

import config as cfg
from handlers import (
    handle_streamlit_none,
    handle_streamlit_json,
    handle_streamlit_ndarray,
    handle_streamlit_df,
    handle_streamlit_pd_series,
)

from utils import PickleLoader, is_json_serializable, ExceptionUnsafePickle


class PickleViewerApp:
    def __init__(self):
        self.BASE_DIR = Path(__file__).resolve().parent
        self.LOGO_PATH = (self.BASE_DIR.parent / "media" / "picklevw.png").resolve()

    @staticmethod
    def set_gui_page_config(layout, page_title, page_icon):
        st.set_page_config(layout=layout, page_title=page_title, page_icon=page_icon)

    @staticmethod
    def set_gui_logo(image, size):
        st.logo(image=image, size=size)

    @staticmethod
    def set_gui_html(body):
        st.html(body=body)

    def setup_page(self) -> None:
        """
        Sets up the Streamlit webpage configuration.

        :param self: The instance of the class where the method is defined.
        :type self: object

        :return: None
        """
        PickleViewerApp.set_gui_page_config(
            layout=cfg.UI["layout"],
            page_title=cfg.UI["title"],
            page_icon=cfg.UI["icon"]
        )
        PickleViewerApp.set_gui_logo(self.LOGO_PATH, size=cfg.UI["logo_size"])
        PickleViewerApp.set_gui_html(
            cfg.MESSAGES["setup_page_html"].format(
                url=cfg.UI["PICKLE_DOCS_URL"],
                version=cfg.CONFIG["version"]
            )
        )

    @staticmethod
    def upload_file() -> UploadedFile | list[UploadedFile] | None:
        """
        Uploads a file through the Streamlit file uploader component and returns the uploaded
        file(s), or None if no file is uploaded. It supports multiple file extensions based on the
        configuration.

        The method interacts with the user interface component to allow users to upload files and
        handles various file types, visibility, and other configurations as defined in the

        application settings.

        :rtype: UploadedFile | list[UploadedFile] | None
        :return: Uploaded file object if a single file is uploaded, a list of UploadedFile objects
            for multiple files, or None if no file is uploaded.
        """
        return st.file_uploader(
            cfg.MESSAGES["UPLOAD_PROMPT"],
            type=cfg.UI["file_extensions"],
            label_visibility="hidden"
        )

    @staticmethod
    def display_content(obj, were_spared_objs, is_dataframe):
        """
        Displays the content of a given object using various rendering methods depending on the type
        of the object. The function utilizes Streamlit for rendering output to the user interface
        and provides fallbacks where applicable.

        :param obj: The object to be displayed. It can be a pandas DataFrame, pandas Series or a
        JSON-serializable object. Certain unsupported types may emit warnings.
        :type obj: object
        :param were_spared_objs: Boolean flag indicating whether objects formatted as JSON will be
            unquoted for display.
        :type were_spared_objs: bool
        :param is_dataframe: Boolean flag indicating whether the object should be treated as a
            DataFrame.
        :type is_dataframe: bool
        :return: None
        :rtype: None
        """
        try:
            st.markdown(cfg.MESSAGES["CONTENT_DISPLAY"])

            if not is_dataframe and obj is None:
                handle_streamlit_none()
                return

            if isinstance(obj, pd.DataFrame):
                handle_streamlit_df(obj)

            elif isinstance(obj, pd.Series):
                handle_streamlit_pd_series(obj)

            elif isinstance(obj, np.ndarray):
                handle_streamlit_ndarray(obj)

            elif is_json_serializable(obj):
                handle_streamlit_json(obj, were_spared_objs)
            else:
                st.warning(cfg.MESSAGES["NOT_JSON_WARNING"])
        except Exception as ex:
            if cfg.CONFIG["DEBUG_MODE"]:
                st.error(f"Display Error: {ex}")

    def process_file(self, uploaded_file, allow_unsafe_file: bool) -> None:
        """
        Handles the processing of an uploaded file by initializing a PickleLoader instance with the
        provided file and determining its content. It then displays the content using the
        `display_content` method, handling both standard data and dataframes.

        If an error occurs during the loading process, it will handle specific unsafe pickle
        exceptions or general errors by showing appropriate messages to the user.

        :param uploaded_file: The file provided by the user for processing.
        :type uploaded_file: Any
        :param allow_unsafe_file: Indicates whether unsafe files are allowed to be processed.
        :type allow_unsafe_file: bool
        :raises ExceptionUnsafePickle: Custom exception raised when unsafe pickle operations
            are encountered.
        :raises Exception: Generic exceptions raised during the loading process.
        :return: None
        """
        try:
            loader = PickleLoader(uploaded_file, allow_unsafe_file=allow_unsafe_file)
            obj, were_spared_objs, is_dataframe = loader.load()
            self.display_content(obj, were_spared_objs, is_dataframe)
        except ExceptionUnsafePickle as err:
            st.error(str(err))
            st.stop()
        except (IOError, OSError) as io_err:
            if cfg.CONFIG["DEBUG_MODE"]:
                st.error(f"File access error: {io_err}")
        except Exception as ex:
            st.error(cfg.MESSAGES["GENERIC_LOAD_ERROR"])
            if cfg.CONFIG["DEBUG_MODE"]:
                st.exception(ex)

    def run(self) -> None:
        """
        Handles the primary operation flow for setting up a page, managing user preferences, and
        processing an uploaded file. This method initializes the necessary states and toggles,
        presents warnings where applicable, and ensures a secure or unsafe file upload based on
        configuration and user input.

        :return: None
        """
        self.setup_page()

        if "allow_unsafe_file" not in st.session_state:
            st.session_state.allow_unsafe_file = cfg.CONFIG["allow_unsafe"]

        allow_unsafe_file = st.toggle(
            cfg.MESSAGES["TOGGLER_TEXT"],
            key="allow_unsafe_file",
            help=cfg.MESSAGES["TOGGLER_HELP"],
            disabled=cfg.CONFIG["always_disallow_unsafe"]
        )

        if allow_unsafe_file:
            st.warning(cfg.MESSAGES["UNSAFE_WARNING"])

        uploaded_file = self.upload_file()
        if uploaded_file:
            self.process_file(uploaded_file, allow_unsafe_file)


if __name__ == "__main__":
    app = PickleViewerApp()
    app.run()
