import streamlit as st
import pandas as pd

import config as cfg


def handle_streamlit_pd_series(obj):
    st.write(f"Pandas Series: **{obj.name or 'unnamed'}**, {len(obj)} elements")
    st.dataframe(obj.to_frame())
    if pd.api.types.is_numeric_dtype(obj):
        st.markdown(cfg.MESSAGES["CHART"])
        st.line_chart(obj)
