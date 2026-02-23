from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from src.config import OUTPUT_DIR
from src.reco.engine import build_artifacts, recommend
from src.ui import render_sidebar
from src.utils import load_css, normalize_txt, pick_poster_url, read_csv_clean_columns

st.set_page_config(page_title="Recommandations", layout="wide")
load_css()
render_sidebar()

st.markdown(
    """
    <div style="
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 18px;
        padding: 18px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.35);
        margin-bottom: 14px;">
      <h3 style="margin:0 0 8px 0;">🎬 Recommandations</h3>
      <p style="margin:0;color:#A8A8C0;">Choisis un film, fixe des filtres, puis affiche 2 recommandations par catégorie.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

CSV_PATH = OUTPUT_DIR / "10_final_imdb_tmdb.csv"


@st.cache_data(show_spinner=False)
def load_df(path: str) -> pd.DataFrame:
    return read_csv_clean_columns(path)


@st.cache_resource(show_spinner=True)
def load_artifacts(path: str) -> dict:
    df = load_df(path)
    return build_artifacts(df)


@st.cache_data(show_spinner=False)
def build_title_index(df: pd.DataFrame) -> pd.DataFrame:
    tmp = df[["ID", "Titre", "Année_de_sortie", "Réalisateurs"]].copy()

    tmp["title"] = tmp["Titre"].astype(str).str.strip()
    tmp = tmp[tmp["title"] != ""]

    tmp["year"] = tmp["Année_de_sortie"].astype(int)
    tmp["director"] = tmp["Réalisateurs"].astype(str).str.strip()

    tmp["key"] = tmp["title"].map(lambda x: normalize_txt(x, collapse_spaces=True))
    tmp["movie_key"] = tmp["title"] + "||" + tmp["year"].astype(str) + "||" + tmp["director"]

    tmp["ID"] = tmp["ID"].astype(str)
    tmp = tmp.drop_duplicates("ID").reset_index(drop=True)

    return tmp[["ID", "movie_key", "title", "year", "director", "key"]]


def get_suggestions(title_index: pd.DataFrame, typed: str, limit: int = 10) -> pd.DataFrame:
    q = normalize_txt(typed, collapse_spaces=True)
    if len(q) < 2:
        return title_index.iloc[0:0]

    keys = title_index["key"]
    starts = title_index[keys.str.startswith(q)]
    if len(starts) >= limit:
        return starts.head(limit)

    contains = title_index[keys.str.contains(q)]
    return pd.concat([starts, contains]).drop_duplicates("ID").head(limit)


def get_forced_2x3_recos(
    artifacts: dict,
    *,
    movie_id: Any,
    year_min: int,
    year_max: int,
    min_rating: float | None,
    base_top_n: int = 800,
    candidate_k: int = 4000,
) -> pd.DataFrame:
    target_order = ["Très populaire", "Populaire", "Peu populaire"]
    order_map = {"Très populaire": 0, "Populaire": 1, "Peu populaire": 2}

    reco_df = recommend(
        artifacts,
        movie_id=movie_id,
        year_min=year_min,
        year_max=year_max,
        min_rating=min_rating,
        top_n=base_top_n,
        candidate_k=candidate_k,
        gated_lock=True,
    )

    tmp = reco_df[reco_df["Popularité"].isin(target_order)].copy()
    tmp = tmp.sort_values("distance_cosine", ascending=True)

    selected = tmp.groupby("Popularité", sort=False).head(2).copy()
    selected["__cat_order"] = selected["Popularité"].map(order_map).astype(int)

    selected = selected.sort_values(["__cat_order", "distance_cosine"], ascending=[True, True])
    return selected.drop(columns="__cat_order")



df = load_df(str(CSV_PATH))
title_index = build_title_index(df)

st.session_state.setdefault("selected_movie_id", "")
st.session_state.setdefault("selected_title", "")
st.session_state.setdefault("reco_df", None)



col1, col2, col3 = st.columns([2.2, 1.2, 1.2], vertical_alignment="top")

with col1:
    typed = st.text_input("Film de référence (titre)", placeholder="Ex: Avatar").strip()
    sug_df = get_suggestions(title_index, typed, limit=10)

    if sug_df.empty:
        st.caption("Tape au moins 2 lettres pour afficher des suggestions.")
    else:
        options = sug_df.to_dict("records")

        def fmt(o: dict) -> str:
            return f"{o['title']} ({o['year']}) — {o['director'] or '—'}"

        chosen = st.selectbox("Suggestions", options=options, format_func=fmt, index=0)

        st.session_state.selected_movie_id = chosen["ID"]
        st.session_state.selected_title = chosen["title"]

st.markdown(f"**Film sélectionné :** {st.session_state.selected_title or '—'}")

with col2:
    year_min, year_max = st.slider(
        "Période de sortie (recommandations)",
        min_value=1950,
        max_value=2025,
        value=(1950, 2025),
        step=1,
    )

with col3:
    min_rating = st.number_input(
        "Note minimale (recommandations)",
        min_value=0.0,
        max_value=10.0,
        value=0.0,
        step=0.1,
        help="0.0 = pas de filtre. Sinon, les reco doivent avoir au moins cette note.",
    )

run = st.button("Lancer la recommandation", type="primary")

if run:
    artifacts = load_artifacts(str(CSV_PATH))
    movie_id = st.session_state.selected_movie_id
    if not movie_id:
        st.stop()

    st.session_state.reco_df = get_forced_2x3_recos(
        artifacts,
        movie_id=movie_id,
        year_min=int(year_min),
        year_max=int(year_max),
        min_rating=float(min_rating) if float(min_rating) > 0 else None,
    )

reco_df = st.session_state.reco_df
if reco_df is not None:
    st.subheader("Recommandations (2 par catégorie de popularité)")

    target_order = ["Très populaire", "Populaire", "Peu populaire"]
    c1, c2, c3 = st.columns(3, vertical_alignment="top")
    col_map = {"Très populaire": c1, "Populaire": c2, "Peu populaire": c3}

    for cat in target_order:
        with col_map[cat]:
            st.markdown(f"### {cat}")

            block = reco_df[reco_df["Popularité"] == cat].head(2)
            if block.empty:
                st.caption("Aucun résultat.")
                continue

            for _, row in block.iterrows():
                poster_url = pick_poster_url(row)

                title = row.get("Titre", "—")
                year = row.get("Année_de_sortie", "—")
                rating = row.get("Note_moyenne", "—")
                dist = row.get("distance_cosine", "—")

                with st.container(border=True):
                    if poster_url:
                        st.image(poster_url, width="stretch")
                    else:
                        st.caption("Poster indisponible")

                    st.markdown(f"**{title}**")
                    st.caption(f"Année: {year} • Note: {rating} • Distance cosine: {dist}")

                    st.caption(f"Genre: {row.get('Genre', '—')}")
                    st.caption(f"Réal: {row.get('Réalisateurs', '—')}")

                    st.page_link(
                        "pages/Film_details.py",
                        label="Voir la fiche",
                        query_params={"id": str(row["ID"])},
                    )