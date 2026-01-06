import streamlit as st
import numpy as np
import pandas as pd

import config as cfg


def handle_streamlit_ndarray(obj: np.ndarray):
    st.write(f"NumPy ndarray: shape = {obj.shape}, dtype = {obj.dtype}")

    if obj.ndim == 1:
        st.dataframe(pd.DataFrame(obj, columns=["Values"]))
        if np.issubdtype(obj.dtype, np.number):
            st.markdown(cfg.MESSAGES["CHART"])
            st.line_chart(obj)

    elif obj.ndim == 2:
        st.dataframe(pd.DataFrame(obj))
        if np.issubdtype(obj.dtype, np.number):
            st.markdown(cfg.MESSAGES["CHART"])
            st.line_chart(pd.DataFrame(obj))

    else:
        st.warning("NumPy array has more than 2 dimensions and cannot be displayed directly.")
