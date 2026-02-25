from __future__ import annotations

import streamlit as st

from src.ui import render_sidebar
from src.utils import load_css


st.set_page_config(
    page_title="IMDb Recommender",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_css()
render_sidebar()
st.image("assets/logo_noir.png")
st.divider()
st.subheader("🚀 Commencer")

st.page_link("pages/Reco_ML.py", label="Aller à la page Recommandations", icon="✨")
st.page_link("pages/Catalogue.py", label="Aller à la page Catalogue", icon="📚")
st.page_link("pages/Espace_client.py", label="Aller à l’Espace client", icon="👤")
