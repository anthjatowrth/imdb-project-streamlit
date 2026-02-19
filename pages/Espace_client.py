from __future__ import annotations

import streamlit as st

from src.ui import render_sidebar
from src.utils import load_css


st.set_page_config(page_title="Espace client", layout="wide")
load_css()
render_sidebar()

st.title("👤 Espace client")
st.info("Page en construction.")