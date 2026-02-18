from __future__ import annotations
import streamlit as st
from src.ui import render_sidebar
from pathlib import Path

from src.utils import load_css, clean_text

import sys
from pathlib import Path

st.set_page_config(page_title="IMDB App", layout="wide")

pages = [
    st.Page("pages/Catalogue.py", title="Catalogue", icon="📚"),
    st.Page("pages/Reco_ML.py", title="Recommandations", icon="🎬"),
]

pg = st.navigation(pages)
pg.run()

sys.path.append(str(Path(__file__).parent))

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

render_sidebar()

st.set_page_config(
    page_title="IMDb Recommender",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state = "expanded"
)



col_logo, col_title = st.columns([1, 6])
with col_logo:
  
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