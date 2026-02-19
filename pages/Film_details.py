from __future__ import annotations

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


def _get_query_param(name: str) -> str:
    """Compatible st.query_params + fallback ancien API."""
    try:
        qp = st.query_params
        v = qp.get(name, "")
        # st.query_params retourne déjà str dans les versions récentes
        return str(v).strip()
    except Exception:
        qp = st.experimental_get_query_params()
        v = qp.get(name, [""])
        if isinstance(v, list):
            v = v[0] if v else ""
        return str(v).strip()


def _movie_label(row: pd.Series) -> str:
    title = str(row.get("Titre", "—")).strip() or "—"
    year = row.get("Année_de_sortie", None)
    try:
        y = str(int(float(year))) if pd.notna(year) else "—"
    except Exception:
        y = "—"
    directors = str(row.get("Réalisateurs", "")).strip()
    director_main = directors.split(",")[0].strip() if directors else ""
    director_main = director_main if director_main else "—"
    return f"{title} ({y}) — {director_main}"


df = load_df()

# --- Lire params : ID prioritaire, sinon titre ---
id_param = _get_query_param("id")
title_param = _get_query_param("title")

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

# ---------------------------------------
# Sélection du film (robuste aux homonymes)
# ---------------------------------------
movie = None

# 1) si ID dans l'URL : match exact
if id_param:
    if "ID" not in df.columns:
        st.error("La colonne 'ID' est absente du CSV, impossible d'ouvrir une fiche par ID.")
        st.stop()

    mask = df["ID"].astype(str).eq(str(id_param))
    if mask.any():
        movie = df.loc[mask].iloc[0]
    else:
        st.error("Film introuvable : l'ID transmis dans l’URL ne correspond à aucun film.")
        st.stop()

# 2) sinon, fallback sur title (avec gestion d'ambiguïté)
if movie is None:
    if not title_param:
        st.info("Aucun film n’a été sélectionné via l’URL. Choisis un film ci-dessous :")

        # On propose directement une sélection robuste (ID caché)
        if "ID" in df.columns:
            tmp = df[["ID", "Titre", "Année_de_sortie", "Réalisateurs"]].copy()
            tmp["Titre"] = tmp["Titre"].fillna("").astype(str).str.strip()
            tmp = tmp[tmp["Titre"] != ""]
            tmp["Année_de_sortie"] = pd.to_numeric(tmp["Année_de_sortie"], errors="coerce").astype("Int64")
            tmp["Réalisateurs"] = tmp["Réalisateurs"].fillna("").astype(str).str.strip()

            # options = IDs, label joli
            tmp["ID"] = tmp["ID"].astype(str)
            id_options = tmp["ID"].drop_duplicates().tolist()
            id_to_row = {r["ID"]: r for _, r in tmp.drop_duplicates("ID").iterrows()}

            chosen_id = st.selectbox(
                "Choisir un film",
                options=id_options,
                format_func=lambda mid: _movie_label(id_to_row[mid]),
                index=0,
            )
            # set movie
            mask = df["ID"].astype(str).eq(str(chosen_id))
            movie = df.loc[mask].iloc[0]
        else:
            # fallback simple si pas d'ID (moins robuste)
            titles = df["Titre"].dropna().astype(str).sort_values().unique()
            chosen = st.selectbox("Choisir un film", titles, index=0)
            title_param = chosen

    if movie is None and title_param:
        # Tentative ancienne : find_movie_row (peut être ambigu)
        # On gère l'ambiguïté proprement si plusieurs titres matchent.
        if "Titre" not in df.columns:
            st.error("Colonne 'Titre' absente.")
            st.stop()

        norm_t = str(title_param).strip().lower()
        matches = df[df["Titre"].astype(str).str.strip().str.lower().eq(norm_t)].copy()

        if matches.empty:
            st.error("Film introuvable. Vérifie le titre transmis dans l’URL.")
            st.stop()

        if len(matches) == 1:
            movie = matches.iloc[0]
        else:
            st.warning("Titre ambigu : plusieurs films portent ce titre. Choisis le bon :")

            # Si ID disponible → choix robuste
            if "ID" in matches.columns:
                matches = matches.copy()
                matches["ID"] = matches["ID"].astype(str)
                id_options = matches["ID"].drop_duplicates().tolist()
                id_to_row = {r["ID"]: r for _, r in matches.drop_duplicates("ID").iterrows()}

                chosen_id = st.selectbox(
                    "Choisir la bonne version",
                    options=id_options,
                    format_func=lambda mid: _movie_label(id_to_row[mid]),
                    index=0,
                )
                mask = df["ID"].astype(str).eq(str(chosen_id))
                movie = df.loc[mask].iloc[0]
            else:
                # Fallback si pas d'ID : choix par (année + réal)
                matches = matches.reset_index(drop=True)
                options = list(range(len(matches)))
                chosen_i = st.selectbox(
                    "Choisir la bonne version",
                    options=options,
                    format_func=lambda i: _movie_label(matches.iloc[int(i)]),
                    index=0,
                )
                movie = matches.iloc[int(chosen_i)]

# Sécurité
if movie is None:
    st.error("Impossible de déterminer le film à afficher.")
    st.stop()


# --------------------
# Affichage (inchangé)
# --------------------
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
    st.caption(
        "Astuce : tu peux arriver ici via un lien comme `Film_details?id=12345` "
        "(ou l'ancien `?title=Inception`, mais `id` évite les homonymes)."
    )
