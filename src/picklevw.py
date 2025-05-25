import os
import json
import re

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile

import config as cfg
from utils import PickleLoader, is_json_serializable, ExceptionUnsafePickle


class PickleViewerApp:
    def __init__(self):
        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.LOGO_PATH = os.path.join(self.BASE_DIR, "..", "media", "picklevw.png")

    def setup_page(self) -> None:
        ui = cfg.UI
        st.set_page_config(layout=ui["layout"], page_title=ui["title"], page_icon=ui["icon"])
        st.logo(self.LOGO_PATH, size=ui["logo_size"])
        st.html(cfg.MESSAGES["setup_page_html"].format(url=cfg.UI["PICKLE_DOCS_URL"], version=cfg.CONFIG["version"]))

    @staticmethod
    def upload_file() -> UploadedFile | list[UploadedFile] | None:
        ui = cfg.UI
        return st.file_uploader(
            cfg.MESSAGES["UPLOAD_PROMPT"],
            type=ui["file_extensions"],
            label_visibility="hidden"
        )

    @staticmethod
    def display_content(obj, were_spared_objs, is_dataframe):
        st.markdown(cfg.MESSAGES["CONTENT_DISPLAY"])

        if not is_dataframe and obj is None:
            st.warning(cfg.MESSAGES["GENERIC_LOAD_ERROR"])
            return

        if isinstance(obj, pd.DataFrame):
            st.write(cfg.MESSAGES["row_col_summary"].format(rows=len(obj), cols=len(obj.columns)))
            st.dataframe(obj)

        elif isinstance(obj, pd.Series):
            st.write(f"Pandas Series: **{obj.name or 'unnamed'}**, {len(obj)} elements")
            st.dataframe(obj.to_frame())
            if pd.api.types.is_numeric_dtype(obj):
                st.markdown(cfg.MESSAGES["CHART"])
                st.line_chart(obj)

        elif isinstance(obj, np.ndarray):
            st.write(f"NumPy Array: shape {obj.shape}, dtype {obj.dtype}")

            # Detect image-like arrays
            if obj.ndim == 2:  # Grayscale
                st.image(obj, caption="Grayscale image", use_column_width=True)
            elif obj.ndim == 3 and obj.shape[2] in (3, 4):  # RGB or RGBA
                st.image(obj, caption="Color image", use_column_width=True)
            else:
                # Show as table
                try:
                    st.dataframe(pd.DataFrame(obj))
                except Exception:
                    st.warning("Cannot render array as table.")

                # Fallback to matplotlib rendering
                fig, ax = plt.subplots()
                ax.imshow(obj, aspect='auto', cmap='viridis')
                ax.set_title("Matplotlib Visualization")
                st.pyplot(fig)

        elif is_json_serializable(obj):
            formatted = json.dumps(obj, indent=4)
            if were_spared_objs:
                formatted = re.sub(r'^"(.*)"$', r"\1", formatted)
            st.code(formatted, language="json")

        else:
            st.warning(cfg.MESSAGES["NOT_JSON_WARNING"])

    def handle_file(self, uploaded_file, allow_unsafe_file: bool) -> None:
        try:
            loader = PickleLoader(uploaded_file, allow_unsafe_file=allow_unsafe_file)
            obj, were_spared_objs, is_dataframe = loader.load()
            self.display_content(obj, were_spared_objs, is_dataframe)
        except ExceptionUnsafePickle as err:
            st.error(str(err))
            st.stop()
        except Exception:
            st.warning(cfg.MESSAGES["GENERIC_LOAD_ERROR"])

    def run(self) -> None:
        self.setup_page()

        if "allow_unsafe_file" not in st.session_state:
            st.session_state.allow_unsafe_file = cfg.CONFIG["allow_unsafe"]

        allow_unsafe_file = st.toggle(
            cfg.MESSAGES["TOGGLER_TEXT"],
            value=st.session_state.allow_unsafe_file,
            key="allow_unsafe_file",
            help=cfg.MESSAGES["TOGGLER_HELP"],
            disabled=cfg.CONFIG["always_disallow_unsafe"]
        )

        if allow_unsafe_file:
            st.warning(cfg.MESSAGES["UNSAFE_WARNING"])

        uploaded_file = self.upload_file()
        if uploaded_file:
            self.handle_file(uploaded_file, allow_unsafe_file)


if __name__ == "__main__":
    app = PickleViewerApp()
    app.run()
