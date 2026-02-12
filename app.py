from __future__ import annotations
import streamlit as st
from src.ui import render_sidebar
# -----------------------------
# Page config
# -----------------------------
render_sidebar()

st.set_page_config(
    page_title="IMDb Recommender",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state = "expanded"
)

# -----------------------------
# Helpers
# -----------------------------
def clean_text(s: str) -> str:
    return " ".join(s.strip().split())




# -----------------------------
# Header
# -----------------------------
col_logo, col_title = st.columns([1, 6])
with col_logo:
    # Tu peux remplacer par ton logo local : st.image("assets/logo.png", width=90)
    st.markdown("## 🎬")
with col_title:
    st.title("IMDb Recommender")
    st.caption(
        "Une app Streamlit pour recommander des films en fonction de tes préférences "
        "(années, genres, réalisateur, film favori…)."
    )
    st.write("Coucou")
st.divider()


