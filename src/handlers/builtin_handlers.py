import json
import re

import streamlit as st
import config as cfg


def handle_streamlit_none():
    st.warning(cfg.MESSAGES["GENERIC_LOAD_ERROR"])


def handle_streamlit_json(obj, were_spared_objs):
    formatted = json.dumps(obj, indent=4)
    if were_spared_objs:
        formatted = re.sub(r'^"(.*)"$', r"\1", formatted)
    st.code(formatted, language="json")
