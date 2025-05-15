"""
Streamlit web application for inspecting and visualizing Python pickle files.

This application provides a user-friendly interface to upload and inspect `.pkl`, `.pickle`, or
`.gz` (gzip-compressed pickle) files. It safely loads pickle data using the `fickling`-enhanced
loader and renders the output either as a table (for pandas DataFrames) or as formatted code
(for other Python objects). It includes support for JSON formatting and object pretty-printing.
"""

import os
import json
import re
import reprlib
from pickle import UnpicklingError

import streamlit as st
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
        A simple <a href="{PICKLE_DOCS_URL}" target="_blank">Pickle</a> file viewer. MIT Licensed. v1.1.1
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
        obj, were_spared_objs = load_pickle(uploaded_file)
        st.markdown(f"**Content**")
        if is_json_serializable(obj):
            formatted = json.dumps(obj, indent=4)
            if were_spared_objs:
                formatted = re.sub(r'^\"(.*)\"$', r'\1', formatted)
            st.code(formatted, language="json")
    except (UnpicklingError, json.JSONDecodeError) as err:
        st.error(f"Invalid file content: {str(err)}")
    except Exception as ex:
        st.error(str(ex))
