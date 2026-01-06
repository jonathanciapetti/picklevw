import streamlit as st

import config as cfg


def handle_streamlit_df(obj):
    st.write(cfg.MESSAGES["row_col_summary"].format(rows=len(obj), cols=len(obj.columns)))
    st.dataframe(obj)
