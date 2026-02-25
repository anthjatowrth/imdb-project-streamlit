from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from src.config import OUTPUT_DIR
from src.reco.engine import build_artifacts, recommend
from src.ui import render_sidebar
from src.utils import load_css, pick_poster_url, read_csv_clean_columns

CSV_PATH = OUTPUT_DIR / "10_final_imdb_tmdb.csv"

st.set_page_config(page_title="Recommandations", layout="wide")
load_css()


@st.cache_data(show_spinner=False)
def load_df(path: str) -> pd.DataFrame:
    return read_csv_clean_columns(path)


@st.cache_resource(show_spinner=True)
def load_artifacts(path: str) -> dict:
    df_ = load_df(path)
    return build_artifacts(df_)


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
def _row_by_id(df_: pd.DataFrame, movie_id: str) -> pd.Series | None:
    if not movie_id:
        return None
    tmp = df_[df_["ID"].astype(str) == str(movie_id)]
    if tmp.empty:
        return None
    return tmp.iloc[0]


def render_selected_movie_in_sidebar(df_: pd.DataFrame) -> None:
    movie_id = st.session_state.get("selected_movie_id", "")
    if not movie_id:
        return

    row = _row_by_id(df_, str(movie_id))
    if row is None:
        return

    title = str(row.get("Titre", "—"))
    year = row.get("Année_de_sortie", "—")
    rating = row.get("Note_moyenne", "—")
    votes = _fmt_votes(row.get("Nombre_votes", "—"))
    director = str(row.get("Réalisateurs", "—"))

    poster_url = pick_poster_url(row)
    poster_html = (
        f"<img class='sidebar-picked-poster' src='{poster_url}' alt='poster'/>"
        if poster_url
        else "<div class='sidebar-picked-poster'></div>"
    )

    st.sidebar.markdown(
        f"""
        <div class="sidebar-picked-wrap">
          <div class="sidebar-picked-title">Vous avez choisi</div>
          <div class="sidebar-picked-card">
            {poster_html}
            <div class="sidebar-picked-meta">
              <div class="sidebar-picked-name">{_clip_text(title, 38)}</div>
              <p class="sidebar-picked-sub">{year} • ⭐ {rating} • 👥 {votes}</p>
              <p class="sidebar-picked-sub">{_clip_text(director, 30)}</p>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


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


df = load_df(str(CSV_PATH))
select_options = build_select_index(df)

st.session_state.setdefault("selected_movie_id", "")
st.session_state.setdefault("selected_title", "")
st.session_state.setdefault("reco_df", None)


def sidebar_extra() -> None:
    render_selected_movie_in_sidebar(df)


render_sidebar(extra=sidebar_extra)

st.markdown(
    """
    <style>
    .page-title{
      text-align:center;
      margin: 10px 0 80px 0;
      font-family: 'Bebas Neue','Impact',sans-serif;
      font-size: 3.4rem;
      letter-spacing: 0.10em;
      color: var(--text-primary);
      line-height: 1;
    }
    .page-intro{
      text-align:left;
      max-width: none;
      margin: 0 0 20px 0;
      padding: 0 6px;
      color: var(--text-secondary);
      font-size: 1.05rem;
      line-height: 1.0;
    }
    .intro-gap{ height: 22px; }

    .cat-gap{ height: 28px; }

    [data-testid="stVerticalBlockBorderWrapper"]:has(.cat-marker),
    [data-testid="stVerticalBlockBorderWrapper"]:has(.cat-marker) > div{
      padding: 18px 18px !important;
      border-radius: 22px !important;
      box-shadow: 0 14px 34px rgba(0,0,0,0.40) !important;
      border: 1px solid rgba(255,255,255,0.18) !important;
      position: relative;
      overflow: hidden;
      isolation: isolate;
      background: rgba(15,14,26,0.92) !important;
      backdrop-filter: blur(8px);
      -webkit-backdrop-filter: blur(8px);
    }

    [data-testid="stVerticalBlockBorderWrapper"]:has(.cat-marker)::before{
      content:"";
      position:absolute;
      inset:0;
      opacity: 0.90;
      pointer-events:none;
      background:
        radial-gradient(circle at 18% 10%, rgba(123,104,238,0.35), transparent 65%),
        radial-gradient(circle at 85% 0%, rgba(232,160,32,0.20), transparent 60%);
      z-index: 0;
    }

    [data-testid="stVerticalBlockBorderWrapper"]:has(.cat-marker) *{
      position: relative;
      z-index: 1;
    }

    .cat-marker{ display:none; }

    [data-testid="stVerticalBlockBorderWrapper"]:has(.cat-marker.tres),
    [data-testid="stVerticalBlockBorderWrapper"]:has(.cat-marker.tres) > div{
      border-left: 10px solid rgba(46, 204, 113, 0.95) !important;
      background: rgba(15,14,26,0.94) !important;
    }

    [data-testid="stVerticalBlockBorderWrapper"]:has(.cat-marker.pop),
    [data-testid="stVerticalBlockBorderWrapper"]:has(.cat-marker.pop) > div{
      border-left: 10px solid rgba(232, 160, 32, 0.95) !important;
      background: rgba(15,14,26,0.94) !important;
    }

    [data-testid="stVerticalBlockBorderWrapper"]:has(.cat-marker.peu),
    [data-testid="stVerticalBlockBorderWrapper"]:has(.cat-marker.peu) > div{
      border-left: 10px solid rgba(231, 76, 60, 0.95) !important;
      background: rgba(15,14,26,0.94) !important;
    }

    .cat-title{
      margin: 0 0 8px 0;
      font-family: 'Bebas Neue','Impact',sans-serif !important;
      letter-spacing: 0.12em;
      font-size: 1.65rem;
      color: var(--text-primary) !important;
      position: relative;
      z-index: 2;
    }
    .cat-sub{
      margin: -2px 0 16px 0;
      color: rgba(168,168,192,0.98);
      font-size: 0.90rem;
      position: relative;
      z-index: 2;
    }

    .reco-card{
      position: relative;
      display:flex;
      flex-direction:column;
      height:100%;
      border-radius: 18px;
      padding: 14px;
      overflow: hidden;
      border: 1px solid rgba(255,255,255,0.12);
      box-shadow: 0 12px 28px rgba(0,0,0,0.38);
      transition: all 0.25s ease;
      background: rgba(255,255,255,0.02);
    }

    .reco-card::before{
      content:"";
      position:absolute;
      inset:-16px;
      background-image: var(--bg, none);
      background-size: cover;
      background-position: center;
      filter: blur(12px) saturate(1.25) contrast(1.15);
      transform: scale(1.08);
      opacity: 0.65;
      pointer-events:none;
    }

    .reco-card::after{
      content:"";
      position:absolute;
      inset:0;
      background: linear-gradient(
        180deg,
        rgba(15,14,26,0.12) 0%,
        rgba(15,14,26,0.48) 55%,
        rgba(15,14,26,0.72) 100%
      );
      pointer-events:none;
    }

    .reco-card > *{ position: relative; z-index: 2; }

    .reco-card:hover{
      border-color: rgba(123, 104, 238, 0.55);
      transform: translateY(-4px);
      box-shadow: 0 0 34px rgba(123, 104, 238, 0.25);
    }

    .reco-poster{
      width:100%;
      height: 340px;
      object-fit: cover;
      border-radius: 14px;
      display:block;
      margin-bottom: 12px;
      background: rgba(255,255,255,0.04);
    }

    .reco-title{
      font-family:'Bebas Neue','Impact',sans-serif;
      font-size: 1.10rem;
      letter-spacing: 0.06em;
      color: var(--text-primary);
      margin: 0 0 6px 0;
    }

    .reco-meta{
      font-size: 0.82rem;
      color: rgba(168,168,192,0.98);
      margin: 0 0 10px 0;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .reco-spacer{ flex-grow: 1; }

    .reco-btn-wrap{
      display:flex;
      justify-content:flex-start;
    }

    .reco-btn{
      display:inline-flex;
      align-items:center;
      justify-content:center;
      min-width: 140px;
      padding: 12px 18px;
      border-radius: 12px;
      border: 1px solid rgba(255,255,255,0.14);
      background: rgba(123,104,238,0.16);
      color: rgba(167,139,250,1);
      text-decoration:none !important;
      font-weight: 700;
      transition: all 0.2s ease;
      backdrop-filter: blur(60px);
    }

    .reco-btn:hover{
      background: rgba(123,104,238,0.28);
      border-color: rgba(123,104,238,0.60);
      color: #ffffff;
      transform: translateY(-1px);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="page-title">Recommandations</div>

    <div class="page-intro">
      Choisis un film que tu aimes (ou un film “référence”), et on te proposera des idées à regarder ensuite.
      Tu peux aussi ajuster les filtres (période, note minimale) pour affiner les suggestions.
      <br/><br/>
      Les résultats sont organisés en trois niveaux de popularité pour te proposer à la fois des valeurs sûres…
      et des pépites moins connues.
    </div>

    <div class="intro-gap"></div>
    """,
    unsafe_allow_html=True,
)

col1, col2, col3 = st.columns([2.2, 1.2, 1.2], vertical_alignment="top")

with col1:
    def fmt(o: dict | None) -> str:
        if not o:
            return "— Sélectionne un film de référence —"
        director = o.get("director") or "—"
        year = o.get("year") or "—"
        return f"{o['title']} ({year}) — {director}"

    chosen = st.selectbox(
        "Film de référence",
        options=[None, *select_options],
        format_func=fmt,
        index=0,
        help="Choisis un film que tu aimes : on s’en servira comme point de départ pour les recommandations.",
    )

    if chosen:
        st.session_state.selected_movie_id = chosen["ID"]
        st.session_state.selected_title = chosen["title"]
    else:
        st.session_state.selected_movie_id = ""
        st.session_state.selected_title = ""

st.markdown(f"**Film sélectionné :** {st.session_state.selected_title or '—'}")

with col2:
    year_min, year_max = st.slider(
        "Période de sortie",
        min_value=1950,
        max_value=2025,
        value=(1950, 2025),
        step=1,
    )

with col3:
    min_rating = st.number_input(
        "Note minimale",
        min_value=0.0,
        max_value=10.0,
        value=0.0,
        step=0.1,
        help="0.0 = pas de filtre. Sinon, on garde uniquement les films au-dessus de cette note.",
    )

run = st.button("Lancer la recommandation", type="primary")

if run:
    artifacts = load_artifacts(str(CSV_PATH))
    movie_id = st.session_state.selected_movie_id
    if not movie_id:
        st.warning("Choisis d’abord un film de référence 🙂")
        st.stop()

    st.session_state.reco_df = get_forced_5x3_recos(
        artifacts,
        movie_id=movie_id,
        year_min=int(year_min),
        year_max=int(year_max),
        min_rating=float(min_rating) if float(min_rating) > 0 else None,
        per_cat=5,
    )

reco_df = st.session_state.reco_df
if reco_df is not None:
    target_order = ["Très populaire", "Populaire", "Peu populaire"]

    cat_info = {
        "Très populaire": ("tres", "Des films très connus, faciles à aimer — parfaits pour une soirée “valeur sûre”."),
        "Populaire": ("pop", "Un bon équilibre : connus, mais avec souvent de belles surprises."),
        "Peu populaire": ("peu", "Des films moins exposés — idéal si tu veux découvrir des pépites."),
    }

    for idx, cat in enumerate(target_order):
        cls, subtitle = cat_info[cat]

        with st.container(border=True):
            st.markdown(f"<div class='cat-marker {cls}'></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='cat-title'>{cat}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='cat-sub'>{subtitle}</div>", unsafe_allow_html=True)

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

                    detail_href = f"Film_details?id={row['ID']}"

                    bg_style = ""
                    if poster_url:
                        bg_style = f"style=\"--bg: url('{poster_url}');\""

                    if poster_url:
                        poster_html = f"<img class='reco-poster' src='{poster_url}' alt='poster'/>"
                    else:
                        poster_html = (
                            "<div class='reco-poster' "
                            "style='display:flex;align-items:center;justify-content:center;'>"
                            "<span style='font-size:0.8rem;color:rgba(168,168,192,0.95)'>Poster indisponible</span>"
                            "</div>"
                        )

                    st.markdown(
                        f"""
                        <div class="reco-card" {bg_style} title="{full_title}">
                          {poster_html}
                          <div class="reco-title">{title_short}</div>
                          <div class="reco-meta">{year} • ⭐ {rating} • 👥 {_fmt_votes(votes)}</div>
                          <div class="reco-spacer"></div>
                          <div class="reco-btn-wrap">
                            <a class="reco-btn" href="{detail_href}">Voir la fiche</a>
                          </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

        if idx < len(target_order) - 1:
            st.markdown("<div class='cat-gap'></div>", unsafe_allow_html=True)