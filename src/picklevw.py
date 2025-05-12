import os
import json
import reprlib
from pickle import UnpicklingError

import streamlit as st
import pandas as pd
from prettyprinter import pformat

from utils import load_pickle, is_json_serializable

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PICKLEVW_LOGO_FILEPATH = os.path.join(BASE_DIR, "..", "media", "picklevw.png")

st.set_page_config(
    layout="wide",
    page_title="picklevw",
    page_icon="🥒",
)

col_1, col_2 = st.columns(2, vertical_alignment="bottom")
with col_1:
    st.image(PICKLEVW_LOGO_FILEPATH, width=200)
    st.html(
        """
        <p style="font-size: 20px; display: inline; text-align: bottom;">
            A simple <a href="https://docs.python.org/3/library/pickle.html" target="_blank">Pickle</a> file viewer
        </p>
        """
    )
with col_2:
    st.html(
        """
            <a style="float:right;" href="https://github.com/jonathanciapetti/picklevw" target="_blank" style="text-decoration: none;">
                <img src="https://github.githubassets.com/assets/GitHub-Logo-ee398b662d42.png" alt="Image 1" height="20">
                <img src="https://github.githubassets.com/assets/GitHub-Mark-ea2971cee799.png" alt="Image 2" height="35">
            </a>
        """
    )

uploaded_file = st.file_uploader(
    # "Upload a Pickle (.pkl, .pickle) or Gzip-Pickle (.gz) File",
    "",
    type=["pkl", "pickle", "gz"]
)

if uploaded_file:
    try:
        obj = load_pickle(uploaded_file)
        st.info(f"The loaded Python object is of type `{type(obj).__name__}`")

        if isinstance(obj, pd.DataFrame):
            st.write(f"Readable: **{len(obj)}** rows and **{len(obj.columns)}** columns")
            st.dataframe(obj)
        else:
            if is_json_serializable(obj):
                formatted = json.dumps(obj, indent=4)
                st.code(formatted, language="json")
            else:
                try:
                    formatted = pformat(obj, indent=4, compact=False)
                except Exception:
                    formatted = reprlib.repr(obj)
                st.code(formatted, language="python")

    except (UnpicklingError, json.JSONDecodeError) as e:
        st.error(f"Invalid file content: {e}")
    except Exception as e:
        st.error(f"Unexpected error: {e}")
