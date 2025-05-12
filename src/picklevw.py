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
PICKLEVW_REPO_URL = "https://github.com/jonathanciapetti/picklevw"
PICKLE_DOCS_URL = "https://docs.python.org/3/library/pickle.html"

st.set_page_config(
    layout="wide",
    page_title="picklevw",
    page_icon="🥒",
)

st.logo(PICKLEVW_LOGO_FILEPATH, size="large")

st.html(
    f"""
    <p style="font-size: 20px; display: inline; text-align: bottom;">
        A simple <a href="{PICKLE_DOCS_URL}" target="_blank">Pickle</a> file viewer. MIT Licensed.
    </p>
    """
)

uploaded_file = st.file_uploader(
    "Upload a Pickle (.pkl, .pickle) or Gzip-Pickle (.gz) File",
    type=["pkl", "pickle", "gz"],
    label_visibility='hidden'
)

if uploaded_file:
    try:
        obj = load_pickle(uploaded_file)
        st.info(f"The loaded Python object is of type `{type(obj).__name__}`")

        if isinstance(obj, pd.DataFrame):
            st.write(
                f"Readable: **{len(obj)}** rows and **{len(obj.columns)}** columns"
            )
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
