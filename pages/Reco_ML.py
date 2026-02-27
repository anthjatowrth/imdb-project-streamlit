from __future__ import annotations

from pathlib import Path
from typing import Any
from urllib.parse import quote

import pandas as pd
import streamlit as st

from src.config import OUTPUT_DIR
from src.reco.engine import build_artifacts, recommend
from src.ui import render_sidebar, clip_text, fmt_votes
from src.utils import load_css, pick_poster_url, read_csv_clean_columns

CSV_PATH = OUTPUT_DIR / "10_final_imdb_tmdb.csv"

st.set_page_config(page_title="Recommandations", layout="wide")
load_css()


ASSETS_DIR = Path(__file__).resolve().parent / "assets"
if not ASSETS_DIR.exists():
    # fallback courant si le fichier est dans un sous-dossier (ex: src/pages/)
    ASSETS_DIR = Path(__file__).resolve().parents[1] / "assets"

BADGE_FILES = {
    "high": "badge_super_similaire.svg",
    "mid": "badge_un_peu_similaire.svg",
    "low": "badge_a_decouvrir.svg",
}

@st.cache_data(show_spinner=False)
def svg_to_data_uri(svg_path: str | Path) -> str:
    """Convertit un SVG local en data URI utilisable dans <img src='...'>."""
    p = Path(svg_path)
    svg_text = p.read_text(encoding="utf-8")
    return "data:image/svg+xml;utf8," + quote(svg_text)

def similarity_badge(distance: Any) -> tuple[str, str]:
    """Retourne (badge_key, label) à partir de distance_cosine."""
    d = pd.to_numeric(distance, errors="coerce")

    # Seuils fixes (à ajuster)
    if d <= 0.40:
        return ("high", "Très similaire")
    elif d <= 0.6:
        return ("mid", "Un peu similaire")
    else:
        return ("low", "Pas trop similaire")

# ── Chargement des données ────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_df() -> pd.DataFrame:
    return read_csv_clean_columns(CSV_PATH)

@st.cache_resource(show_spinner=False)
def load_artifacts() -> dict:
    df_ = load_df()
    return build_artifacts(df_)

@st.cache_data(show_spinner=False)
def _row_by_id(movie_id: str) -> pd.Series | None:
    if not movie_id:
        return None
    df_ = load_df()
    tmp = df_[df_["ID"].astype(str) == str(movie_id)]
    if tmp.empty:
        return None
    return tmp.iloc[0]

@st.cache_data(show_spinner=False)
def build_select_index() -> list[dict]:
    tmp = load_df()[["ID", "Titre", "Année_de_sortie", "Réalisateurs", "Nombre_votes"]].copy()
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

# ── Sidebar ───────────────────────────────────────────────────────────────────
def render_selected_movie_in_sidebar() -> None:
    movie_id = st.session_state.get("selected_movie_id", "")
    if not movie_id:
        return

    row = _row_by_id(str(movie_id))
    if row is None:
        return

    title = str(row.get("Titre", "—"))
    year = row.get("Année_de_sortie", "—")
    rating = row.get("Note_moyenne", "—")
    votes = fmt_votes(row.get("Nombre_votes", "—"))
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
              <div class="sidebar-picked-name">{clip_text(title, 38)}</div>
              <p class="sidebar-picked-sub">{year} • ⭐ {rating} • 👥 {votes}</p>
              <p class="sidebar-picked-sub">{clip_text(director, 30)}</p>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

select_options = build_select_index()

st.session_state.setdefault("selected_movie_id", "")
st.session_state.setdefault("selected_title", "")
st.session_state.setdefault("reco_df", None)

render_sidebar(extra=lambda: render_selected_movie_in_sidebar())

# ── En-tête de page ───────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="page-title">On te recommmande des films !</div>
    <div class="page-intro">
      Choisis un film que tu aimes (ou un film "référence"), et on te proposera des idées à regarder ensuite.
      Tu peux aussi ajuster les filtres (période, note minimale) pour affiner les suggestions.
      <br/><br/>
      Les résultats sont organisés en trois niveaux de popularité pour te proposer à la fois des valeurs sûres…
      et des pépites moins connues.
    </div>
    <div class="intro-gap"></div>
    """,
    unsafe_allow_html=True,
)

# ── Sélection du film de référence ───────────────────────────────────────────
col1, col2, col3 = st.columns([2.2, 1.2, 1.2], vertical_alignment="top")

with col1:
    def fmt(o: dict | None) -> str:
        if not o:
            return "— Sélectionne un film de référence —"
        return f"{o['title']} ({o.get('year', '—')}) — {o.get('director', '—')}"

    chosen = st.selectbox(
        "Film de référence",
        options=[None, *select_options],
        format_func=fmt,
        index=0,
        help="Choisis un film que tu aimes : on s'en servira comme point de départ pour les recommandations.",
    )

    if chosen:
        st.session_state.selected_movie_id = chosen["ID"]
        st.session_state.selected_title = chosen["title"]
    else:
        st.session_state.selected_movie_id = ""
        st.session_state.selected_title = ""

with col2:
    year_min, year_max = st.slider(
        "Période de sortie", min_value=1950, max_value=2025, value=(1950, 2025), step=1,
    )

with col3:
    min_rating = st.number_input(
        "Note minimale", min_value=0.0, max_value=10.0, value=0.0, step=0.1,
        help="0.0 = pas de filtre. Sinon, on garde uniquement les films au-dessus de cette note.",
    )

run = st.button("Lancer la recommandation", type="primary")

if run:
    artifacts = load_artifacts()
    movie_id = st.session_state.selected_movie_id
    if not movie_id:
        st.warning("Choisis d'abord un film de référence 🙂")
        st.stop()

    st.session_state.reco_df = get_forced_5x3_recos(
        artifacts,
        movie_id=movie_id,
        year_min=int(year_min),
        year_max=int(year_max),
        min_rating=float(min_rating) if float(min_rating) > 0 else None,
        per_cat=5,
    )

# ── Affichage des résultats ───────────────────────────────────────────────────
reco_df = st.session_state.reco_df
if reco_df is not None:
    target_order = ["Très populaire", "Populaire", "Peu populaire"]

    cat_info = {
        "Très populaire": ("tres", "🔥 Valeurs sûres",       "Des films très connus, faciles à aimer — parfaits pour une soirée 'valeur sûre'."),
        "Populaire":      ("pop",  "⭐ Belles découvertes",   "Un bon équilibre : connus, mais avec souvent de belles surprises."),
        "Peu populaire":  ("peu",  "💎 Pépites cachées",      "Des films moins exposés — idéal si tu veux découvrir des pépites."),
    }

    for cat in target_order:
        cls, display_title, subtitle = cat_info[cat]
        block = reco_df[reco_df["Popularité"] == cat].head(5)

        with st.container(border=True):
            st.markdown(
                f"""
                <div class="cat-header">
                    <div class="cat-title">{display_title}</div>
                    <div class="cat-sub">{subtitle}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if block.empty:
                st.caption("Aucun résultat.")
            else:
                cols = st.columns(5, gap="small", vertical_alignment="top")

                for i, (_, row) in enumerate(block.iterrows()):
                    with cols[i]:
                        poster_url = pick_poster_url(row)
                        full_title = str(row.get("Titre", "—"))
                        title_short = full_title
                        year = row.get("Année_de_sortie", "—")
                        rating = row.get("Note_moyenne", "—")
                        votes = row.get("Nombre_votes", "—")
                        detail_href = f"Film_details?id={row['ID']}"

                        badge_key, badge_label = similarity_badge(row.get("distance_cosine"))
                        badge_filename = BADGE_FILES.get(badge_key)
                        badge_path = ASSETS_DIR / badge_filename
                        try:
                            badge_uri = svg_to_data_uri(badge_path)
                        except FileNotFoundError:
                            badge_uri = ""

                        bg_style = f"style=\"--bg: url('{poster_url}');\"" if poster_url else ""

                        if poster_url:
                            poster_html = f"<img class='reco-poster' src='{poster_url}' alt='poster'/>"
                        else:
                            poster_html = (
                                "<div class='reco-poster' "
                                "style='display:flex;align-items:center;justify-content:center;'>"
                                "<span style='font-size:0.8rem;color:rgba(168,168,192,0.95)'>Poster indisponible</span>"
                                "</div>"
                            )

                        badge_img_html = (
                            f"<img class='sim-badge-img' src='{badge_uri}' alt='{badge_label}' "
                            f"title='{badge_label} (distance={row.get('distance_cosine')})'/>"
                            if badge_uri
                            else ""
                        )

                        st.markdown(
                            f"""
                            <div class="reco-card" {bg_style} title="{full_title}">
                            {poster_html}
                            <div class="reco-title">{title_short}</div>
                            <div class="reco-meta">{year} • ⭐ {rating} • 👥 {fmt_votes(votes)}</div>
                            <div class="reco-spacer"></div>
                            <div class="reco-btn-wrap">
                                {badge_img_html}
                                <a class="reco-btn" href="{detail_href}">Voir la fiche</a>
                            </div>
                            </div>
                            """,
                            unsafe_allow_html=True,)

        st.markdown("<div class='cat-gap'></div>", unsafe_allow_html=True)