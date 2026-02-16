from __future__ import annotations
import streamlit as st
from src.ui import render_sidebar
from pathlib import Path

def load_css():
    css_path = Path("assets/style.css")
    st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

load_css()
st.markdown(
    """
    <div style="
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 18px;
        padding: 18px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.35);
    ">
      <h3 style="margin:0 0 8px 0;">🎬 Bloc Recommandations</h3>
      <p style="margin:0;color:#A8A8C0;">Choisis un film et génère des suggestions.</p>
    </div>
    """,
    unsafe_allow_html=True
)

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
        "(années, genres, réalisateur, film favori…).")
st.divider()

st.subheader("🚀 Commencer")

st.page_link(
    "pages/Reco_ML.py",
    label="Aller à la page Recommandations",
    icon="🎬"
)
st.page_link(
    "pages/Catalogue.py",
    label="Aller à la page catalogue",
    icon="🎬")