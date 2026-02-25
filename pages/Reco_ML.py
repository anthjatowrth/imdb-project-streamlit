from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from src.config import OUTPUT_DIR
from src.reco.engine import build_artifacts, recommend
from src.ui import render_sidebar
from src.utils import load_css, pick_poster_url, read_csv_clean_columns

# ----------------------------
# Page config + UI shell
# ----------------------------
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
      <p style="margin:0;color:#A8A8C0;">Choisis un film, fixe des filtres, puis affiche 5 recommandations par catégorie.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

CSV_PATH = OUTPUT_DIR / "10_final_imdb_tmdb.csv"


# ----------------------------
# Caching
# ----------------------------
@st.cache_data(show_spinner=False)
def load_df(path: str) -> pd.DataFrame:
    return read_csv_clean_columns(path)


@st.cache_resource(show_spinner=True)
def load_artifacts(path: str) -> dict:
    df_ = load_df(path)
    return build_artifacts(df_)


# ----------------------------
# Helpers
# ----------------------------
def _clip_text(s: Any, max_len: int = 34) -> str:
    txt = str(s) if s is not None else ""
    txt = txt.strip()
    if txt == "" or txt.lower() == "nan":
        return "—"
    if len(txt) <= max_len:
        return txt
    return txt[: max_len - 1].rstrip() + "…"


def _fmt_votes(v: Any) -> str:
    try:
        return f"{int(float(v)):,}".replace(",", " ")
    except Exception:
        return "—"


@st.cache_data(show_spinner=False)
def build_select_index(df_: pd.DataFrame) -> list[dict]:
    tmp = df_[["ID", "Titre", "Année_de_sortie", "Réalisateurs", "Nombre_votes"]].copy()

    tmp["title"] = tmp["Titre"].astype(str).str.strip()
    tmp = tmp[tmp["title"] != ""]

    tmp["year"] = pd.to_numeric(tmp["Année_de_sortie"], errors="coerce").fillna(0).astype(int)
    tmp["director"] = tmp["Réalisateurs"].astype(str).str.strip()
    tmp["votes"] = pd.to_numeric(tmp["Nombre_votes"], errors="coerce").fillna(0).astype(int)

    tmp["ID"] = tmp["ID"].astype(str)

    tmp = tmp.sort_values(["votes", "year", "title"], ascending=[False, False, True])

    return tmp[["ID", "title", "year", "director", "votes"]].to_dict("records")


def get_forced_5x3_recos(
    artifacts: dict,
    *,
    movie_id: Any,
    year_min: int,
    year_max: int,
    min_rating: float | None,
    base_top_n: int = 800,
    candidate_k: int = 4000,
    per_cat: int = 5,
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

    selected = tmp.groupby("Popularité", sort=False).head(per_cat).copy()
    selected["__cat_order"] = selected["Popularité"].map(order_map).astype(int)
    selected = selected.sort_values(["__cat_order", "distance_cosine"], ascending=[True, True])
    return selected.drop(columns="__cat_order")


# ----------------------------
# Mini-card CSS
# ----------------------------
st.markdown(
    """
    <style>
    .reco-grid { margin-top: 8px; margin-bottom: 10px; }

    .mini-card{
      border: 1px solid rgba(255,255,255,0.08);
      background: rgba(255,255,255,0.03);
      border-radius: 14px;
      padding: 10px;
      box-shadow: 0 8px 16px rgba(0,0,0,0.25);
    }

    .mini-poster{
      width: 100%;
      height: 240px;
      object-fit: cover;
      border-radius: 10px;
      display: block;
      margin-bottom: 8px;
      background: rgba(255,255,255,0.04);
    }

    .mini-title{
      font-size: 0.92rem;
      line-height: 1.1;
      margin: 0 0 4px 0;
    }

    .mini-meta{
      font-size: 0.78rem;
      color: rgba(168,168,192,0.95);
      margin: 0;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------
# Data init
# ----------------------------
df = load_df(str(CSV_PATH))
select_options = build_select_index(df)

st.session_state.setdefault("selected_movie_id", "")
st.session_state.setdefault("selected_title", "")
st.session_state.setdefault("reco_df", None)

# ----------------------------
# Controls
# ----------------------------
col1, col2, col3 = st.columns([2.2, 1.2, 1.2], vertical_alignment="top")

with col1:
    def fmt(o: dict) -> str:
        return f"{o['title']} ({o['year']}) — {o['director'] or '—'}"

    chosen = st.selectbox(
        "Film de référence (recherche intégrée)",
        options=select_options,
        format_func=fmt,
        index=0 if select_options else None,
    )

    if chosen:
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
        st.warning("Choisis un film de référence.")
        st.stop()

    st.session_state.reco_df = get_forced_5x3_recos(
        artifacts,
        movie_id=movie_id,
        year_min=int(year_min),
        year_max=int(year_max),
        min_rating=float(min_rating) if float(min_rating) > 0 else None,
        per_cat=5,
    )

# ----------------------------
# Display recos
# ----------------------------
reco_df = st.session_state.reco_df
if reco_df is not None:
    st.markdown(
        """
        <h3 style="
            text-align:center;
            margin-top:10px;
            margin-bottom:20px;
            letter-spacing:0.5px;
        ">
        Recommandations
        </h3>
        """,
        unsafe_allow_html=True,
    )

    target_order = ["Très populaire", "Populaire", "Peu populaire"]

    for cat in target_order:
        st.markdown(f"### {cat}")

        block = reco_df[reco_df["Popularité"] == cat].head(5)
        if block.empty:
            st.caption("Aucun résultat.")
            continue

        cols = st.columns(5, gap="small", vertical_alignment="top")

        for i, (_, row) in enumerate(block.iterrows()):
            with cols[i]:
                poster_url = pick_poster_url(row)

                full_title = str(row.get("Titre", "—"))
                title_short = _clip_text(full_title, max_len=34)

                year = row.get("Année_de_sortie", "—")
                rating = row.get("Note_moyenne", "—")
                votes = row.get("Nombre_votes", "—")

                genre = row.get("Genre", "—")
                director = row.get("Réalisateurs", "—")

                if poster_url:
                    poster_html = f"<img class='mini-poster' src='{poster_url}' alt='poster'/>"
                else:
                    poster_html = (
                        "<div class='mini-poster' "
                        "style='display:flex;align-items:center;justify-content:center;'>"
                        "<span style='font-size:0.8rem;color:rgba(168,168,192,0.95)'>Poster indisponible</span>"
                        "</div>"
                    )

                st.markdown(
                    f"""
                    <div class="mini-card" title="{full_title} • {year} • {director} • {genre}">
                      {poster_html}
                      <div class="mini-title"><b>{title_short}</b></div>
                      <p class="mini-meta">{year} • ⭐ {rating} • 👥 {_fmt_votes(votes)}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                st.page_link(
                    "pages/Film_details.py",
                    label="Voir la fiche",
                    query_params={"id": str(row["ID"])},
                )

        st.markdown("<div class='reco-grid'></div>", unsafe_allow_html=True)