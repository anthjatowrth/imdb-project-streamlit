from __future__ import annotations

import pandas as pd
import streamlit as st

from src.config import OUTPUT_DIR
from src.reco.engine import build_artifacts, recommend
from src.utils import (
    load_css,
    normalize_txt,
    pick_poster_url,
    read_csv_clean_columns,
    title_exists,
)

st.set_page_config(page_title="Recommandations", layout="wide")
load_css()

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


#DATA / CACHE :

@st.cache_data(show_spinner=False)
def load_df(path: str) -> pd.DataFrame:
    return read_csv_clean_columns(path)


@st.cache_resource(show_spinner=True)
def load_artifacts_from_path(path: str) -> dict:
    df = load_df(path)
    return build_artifacts(df)


@st.cache_data(show_spinner=False)
def build_title_index(df: pd.DataFrame) -> pd.DataFrame:
    tmp = df[["Titre", "Année_de_sortie", "Réalisateurs"]].copy()

    tmp["title"] = tmp["Titre"].fillna("").astype(str).str.strip()
    tmp = tmp[tmp["title"] != ""]

    tmp["year"] = pd.to_numeric(tmp["Année_de_sortie"], errors="coerce").astype("Int64")
    tmp["director"] = tmp["Réalisateurs"].fillna("").astype(str).str.strip()

    tmp["key"] = tmp["title"].map(lambda x: normalize_txt(x, collapse_spaces=True))

    tmp["dir_len"] = tmp["director"].str.len()
    tmp = (
        tmp.sort_values(["title", "year", "dir_len"], ascending=[True, False, False])
           .drop_duplicates("title", keep="first")
           .reset_index(drop=True)
    )
    return tmp[["title", "year", "director", "key"]]


def get_suggestions(title_index: pd.DataFrame, typed: str, limit: int = 10) -> pd.DataFrame:
    q = normalize_txt(typed, collapse_spaces=True)
    if len(q) < 2:
        return title_index.iloc[0:0]  # df vide

    keys = title_index["key"]
    starts = title_index[keys.str.startswith(q, na=False)]
    if len(starts) >= limit:
        return starts.head(limit)

    contains = title_index[keys.str.contains(q, na=False)]
    sug = pd.concat([starts, contains]).drop_duplicates("title").head(limit)
    return sug


def get_forced_2x3_recos(
    artifacts: dict,
    *,
    title_query: str,
    year_min: int,
    year_max: int,
    min_rating: float | None,
    base_top_n: int = 800,
    candidate_k: int = 4000,
) -> pd.DataFrame:
    target_order = ["Très populaire", "Populaire", "Peu populaire"]

    reco_df = recommend(
        artifacts,
        title_query=title_query,
        year_min=int(year_min),
        year_max=int(year_max),
        min_rating=min_rating,
        top_n=int(base_top_n),
        candidate_k=int(candidate_k),
    )

    tmp = reco_df[reco_df["Popularité"].isin(target_order)].copy()

    if "distance_cosine" in tmp.columns:
        tmp = tmp.sort_values("distance_cosine", ascending=True)

    selected = tmp.groupby("Popularité", sort=False).head(2).copy()

    selected["__cat_order"] = selected["Popularité"].map(
        {"Très populaire": 0, "Populaire": 1, "Peu populaire": 2}
    ).fillna(99).astype(int)

    sort_cols = ["__cat_order"]
    asc = [True]
    if "distance_cosine" in selected.columns:
        sort_cols.append("distance_cosine")
        asc.append(True)

    selected = selected.sort_values(sort_cols, ascending=asc)
    return selected.drop(columns=["__cat_order"])


df2 = load_df(str(CSV_PATH))
title_index = build_title_index(df2)

st.session_state.setdefault("selected_title", "")
st.session_state.setdefault("typed_title_input", "")
st.session_state.setdefault("reco_df", None)


def pick_title(t: str) -> None:
    st.session_state.selected_title = t
    st.session_state.typed_title_input = t
    st.rerun()


col1, col2, col3 = st.columns([2.2, 1.2, 1.2], vertical_alignment="top")

with col1:
    st.session_state.setdefault("selected_title", "")
    st.session_state.setdefault("typed_title", "")

    typed = st.text_input(
        "Film de référence (titre)",
        key="typed_title",
        placeholder="Ex: Avatar",
    ).strip()

    sug_df = get_suggestions(title_index, typed, limit=10)

    if not sug_df.empty:
        options = sug_df.to_dict("records")

        def fmt(o: dict) -> str:
            year = o["year"]
            y = str(int(year)) if pd.notna(year) else "—"
            director = o["director"] if o["director"] else "—"
            return f"{o['title']} ({y}) — {director}"

        chosen = st.selectbox(
            "Suggestions",
            options=options,
            format_func=fmt,
            index=0,
        )

        st.session_state.selected_title = chosen["title"]
    else:
        st.caption("Tape au moins 2 lettres pour afficher des suggestions.")

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
    with st.spinner("Préparation du moteur de recommandation..."):
        artifacts = load_artifacts_from_path(str(CSV_PATH))
    title_query = (st.session_state.selected_title or "").strip()

    if not title_query:
        st.warning("Sélectionne un titre via les suggestions avant de lancer.")
        st.stop()

    if not title_exists(df2, title_query):
        st.warning("Le film sélectionné n'existe pas dans la base (passe par les suggestions).")
        st.stop()

    try:
        st.session_state.reco_df = get_forced_2x3_recos(
            artifacts,
            title_query=title_query,
            year_min=int(year_min),
            year_max=int(year_max),
            min_rating=float(min_rating) if float(min_rating) > 0 else None,
        )
    except Exception as e:
        st.error(str(e))
        st.stop()


reco_df = st.session_state.reco_df
if reco_df is not None:
    target_order = ["Très populaire", "Populaire", "Peu populaire"]

    st.subheader("Recommandations (2 par catégorie de popularité)")

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

                with st.container(border=700):
                    if poster_url:
                        st.image(poster_url, use_container_width=500)
                    else:
                        st.caption("Poster indisponible")

                    st.markdown(f"**{title}**")
                    st.caption(f"Année: {year} • Note: {rating} • Distance cosine: {dist}")

                    if pd.notna(row.get("Genre", None)):
                        st.caption(f"Genre: {row['Genre']}")
                    if pd.notna(row.get("Réalisateurs", None)):
                        st.caption(f"Réal: {row['Réalisateurs']}")

                    st.page_link(
                        "pages/Film_details.py",
                        label="Voir la fiche",
                        query_params={"title": title},
                    )
