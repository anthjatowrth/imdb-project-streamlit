from __future__ import annotations

import unicodedata
from pathlib import Path

import pandas as pd
import streamlit as st

from src.config import OUTPUT_DIR
from src.ui import render_sidebar
from src.utils import load_css, pick_poster_url, read_csv_clean_columns, find_movie_row


st.set_page_config(page_title="Fiche film", layout="wide")
load_css()
render_sidebar()

@st.cache_data(show_spinner=False)
def load_df() -> pd.DataFrame:
    return read_csv_clean_columns(OUTPUT_DIR / "10_final_imdb_tmdb.csv")

df = load_df()

try:
    qp = st.query_params
    title_param = qp.get("title", "")
except Exception:
    qp = st.experimental_get_query_params()
    title_param = qp.get("title", [""])
    title_param = title_param[0] if isinstance(title_param, list) else title_param

title_param = str(title_param).strip()


st.markdown(
    """
    <div style="
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 18px;
        padding: 18px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.35);
        margin-bottom: 14px;
    ">
      <h3 style="margin:0 0 8px 0;">🎞️ Fiche film</h3>
      <p style="margin:0;color:#A8A8C0;">Page dédiée à un film : affiche toutes les informations disponibles.</p>
    </div>
    """,
    unsafe_allow_html=True,
)


if not title_param:
    st.info("Aucun film n’a été sélectionné via l’URL. Choisis un film ci-dessous :")
    titles = df["Titre"].dropna().astype(str).sort_values().unique()
    chosen = st.selectbox("Choisir un film", titles, index=0)
    title_param = chosen

movie = find_movie_row(df, title_param)

if movie is None:
    st.error("Film introuvable. Vérifie le titre transmis dans l’URL.")
    st.stop()



left, right = st.columns([1.1, 2.2], vertical_alignment="top")

with left:
    poster_url = pick_poster_url(movie)
    if poster_url:
        st.image(poster_url, use_container_width=True)
    else:
        st.caption("Poster indisponible")


    year = movie.get("Année_de_sortie", None)
    rating = movie.get("Note_moyenne", None)
    votes = movie.get("Nombre_de_votes", None)
    duration = movie.get("Durée", None)

    m1, m2 = st.columns(2)
    with m1:
        st.metric("Année", int(year) if pd.notna(year) else "—")
        st.metric("Durée", f"{int(duration)} min" if pd.notna(duration) else "—")
    with m2:
        st.metric("Note", f"{float(rating):.1f}/10" if pd.notna(rating) else "—")
        st.metric("Votes", f"{int(votes):,}".replace(",", " ") if pd.notna(votes) else "—")

    st.divider()
    st.caption(f"Popularité : **{movie.get('Popularité', '—')}**")
    st.caption(f"Pays : **{movie.get('Pays_origine', '—')}**")


with right:
    st.markdown(f"# {movie.get('Titre', '—')}")

    genre = movie.get("Genre", "")
    accroche = movie.get("Accroche", "")
    prod = movie.get("Boite_de_production", "")
    directors = movie.get("Réalisateurs", "")


    chips = []
    if pd.notna(genre) and str(genre).strip():
        chips.append(f"🎭 {genre}")
    if pd.notna(directors) and str(directors).strip():
        chips.append(f"🎬 {directors}")
    if pd.notna(prod) and str(prod).strip():
        chips.append(f"🏢 {prod}")

    if chips:
        st.write(" • ".join(chips))

    if pd.notna(accroche) and str(accroche).strip():
        st.markdown(f"> {accroche}")

    st.divider()


    resume = movie.get("Résumé", "")
    with st.expander("📖 Résumé", expanded=True):
        if pd.notna(resume) and str(resume).strip():
            st.write(resume)
        else:
            st.caption("Aucun résumé.")

    casting = movie.get("Casting", "")
    with st.expander("🧑‍🤝‍🧑 Casting", expanded=False):
        if pd.notna(casting) and str(casting).strip():
            st.write(casting)
        else:
            st.caption("Casting indisponible.")

    st.subheader("Détails")
    details_cols = st.columns(2)

    with details_cols[0]:
        st.write(f"**Genre :** {movie.get('Genre', '—')}")
        st.write(f"**Réalisateurs :** {movie.get('Réalisateurs', '—')}")
        st.write(f"**Pays d'origine :** {movie.get('Pays_origine', '—')}")
        st.write(f"**Popularité :** {movie.get('Popularité', '—')}")

    with details_cols[1]:
        st.write(f"**Boîte de production :** {movie.get('Boite_de_production', '—')}")
        st.write(f"**Année :** {movie.get('Année_de_sortie', '—')}")
        st.write(f"**Durée :** {movie.get('Durée', '—')} min")
        st.write(f"**Note moyenne :** {movie.get('Note_moyenne', '—')}")
        st.write(f"**Nombre de votes :** {movie.get('Nombre_de_votes', '—')}")

    st.divider()
    st.caption("Astuce : tu peux arriver ici via un lien comme `Film_Detail?title=Inception` (encodé URL si besoin).")
