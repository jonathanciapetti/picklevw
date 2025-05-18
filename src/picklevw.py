import os
import json
import re

import streamlit as st

from utils import PickleLoader, is_json_serializable, ExceptionUnsafePickle


class PickleViewerApp:
    def __init__(self):
        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.PICKLEVW_LOGO_FILEPATH = os.path.join(
            self.BASE_DIR, "..", "media", "picklevw.png"
        )
        self.PICKLE_DOCS_URL = "https://docs.python.org/3/library/pickle.html"

    def setup_page(self):
        st.set_page_config(
            layout="wide",
            page_title="picklevw",
            page_icon="🥒",
        )
        st.logo(self.PICKLEVW_LOGO_FILEPATH, size="large")
        st.html(
            f"""
            <p style="font-size: 20px; display: inline; text-align: bottom;">
                A simple <a href="{self.PICKLE_DOCS_URL}" target="_blank">Pickle</a> file viewer. MIT Licensed. v1.2.1
            </p>
            """
        )

    def upload_file(self):
        return st.file_uploader(
            "Upload a Pickle (.pkl, .pickle) or Gzip-Pickle (.gz) File",
            type=["pkl", "pickle", "gz"],
            label_visibility="hidden",
        )

    def display_content(self, obj, were_spared_objs, is_dataframe):
        st.markdown("**Content**")
        if not is_dataframe and not obj:
            st.warning("picklevw could not read the content of this file.")
            return
        if is_dataframe:
            st.write(
                f"Readable: **{len(obj)}** rows and **{len(obj.columns)}** columns"
            )
            st.dataframe(obj)
        elif is_json_serializable(obj):
            formatted = json.dumps(obj, indent=4)
            if were_spared_objs:
                formatted = re.sub(r'^"(.*)"$', r"\1", formatted)
            st.code(formatted, language="json")
        else:
            st.warning("The object is not JSON serializable and is not a DataFrame.")

    def handle_file(self, uploaded_file):
        try:
            loader = PickleLoader(uploaded_file)
            obj, were_spared_objs, is_dataframe = loader.load()
            self.display_content(obj, were_spared_objs, is_dataframe)
        except ExceptionUnsafePickle as err:
            st.error(str(err))
        except Exception as ex:
            st.warning("picklevw could not read the content of this file.")

    def run(self):
        self.setup_page()
        uploaded_file = self.upload_file()
        if uploaded_file:
            self.handle_file(uploaded_file)


if __name__ == "__main__":
    app = PickleViewerApp()
    app.run()
