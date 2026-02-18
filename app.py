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

col_logo, col_title = st.columns([1, 6])
with col_logo:
    st.markdown("## 🎬")
with col_title:
    st.title("IMDb Recommender")
    st.caption(
        "Une app Streamlit pour recommander des films en fonction de tes préférences "
        "(années, genres, réalisateur, film favori…)."
    )

st.divider()
st.subheader("🚀 Commencer")

st.page_link("pages/Reco_ML.py", label="Aller à la page Recommandations", icon="✨")
st.page_link("pages/Catalogue.py", label="Aller à la page Catalogue", icon="📚")
st.page_link("pages/Espace_client.py", label="Aller à l’Espace client", icon="👤")
