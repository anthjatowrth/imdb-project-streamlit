from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st

from src.ui import render_sidebar
from src.config import OUTPUT_DIR
from src.utils import load_css, normalize_txt, read_csv_clean_columns, resolve_poster_url

st.set_page_config(page_title="Catalogue", layout="wide")

if "go_to_title" in st.session_state:
    _ = st.session_state.pop("go_to_title")
    st.switch_page("pages/Film_details.py")

load_css()
render_sidebar()

st.markdown(
    """
    <style>
    .card-wrap{
      position: relative;
      width: 100%;
      aspect-ratio: 2 / 3;
      border-radius: 18px;
      overflow: hidden;
      background: rgba(10,10,16,0.25);
      border: 1px solid rgba(255,255,255,0.14);
      box-shadow: 0 16px 40px rgba(0,0,0,0.35), inset 0 1px 0 rgba(255,255,255,0.06);
      transform: translateZ(0);
      transition: transform 180ms ease, border-color 180ms ease, box-shadow 180ms ease;
    }

    .card-wrap:hover{
      transform: translateY(-2px);
      border-color: rgba(255,255,255,0.22);
      box-shadow: 0 22px 52px rgba(0,0,0,0.42), inset 0 1px 0 rgba(255,255,255,0.08);
    }

    .movie-card{
      position: absolute;
      inset: 0;
      border-radius: 18px;
      overflow: hidden;
      background-image: var(--poster);
      background-repeat: no-repeat;
      background-size: cover;
      background-position: center;
      transform: translateZ(0);
      transition: transform 180ms ease, filter 180ms ease;
      filter: saturate(0.98) contrast(1.03);
    }

    .card-wrap:hover .movie-card{
      transform: scale(1.015);
      filter: saturate(1.05) contrast(1.07);
    }

    .movie-card::before{
      content:"";
      position:absolute;
      inset:0;
      background: radial-gradient(120% 120% at 50% 0%,
                rgba(255,255,255,0.08) 0%,
                rgba(0,0,0,0.20) 55%,
                rgba(0,0,0,0.60) 100%);
      pointer-events:none;
    }

    .movie-meta{
      position:absolute;
      left:0; right:0; bottom:0;
      padding: 14px 14px 12px 14px;
      background: linear-gradient(180deg,
                rgba(0,0,0,0.00) 0%,
                rgba(0,0,0,0.55) 35%,
                rgba(0,0,0,0.85) 100%);
      backdrop-filter: blur(10px);
      -webkit-backdrop-filter: blur(10px);
      pointer-events:none;
    }

    .movie-title{
      font-size: 1.06rem;
      font-weight: 750;
      line-height: 1.15;
      margin: 0 0 6px 0;
      color: rgba(255,255,255,0.95);
      text-shadow: 0 6px 18px rgba(0,0,0,0.55);
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }

    .movie-sub{
      font-size: 0.90rem;
      font-weight: 650;
      color: rgba(255,255,255,0.78);
      margin: 0;
      text-shadow: 0 6px 18px rgba(0,0,0,0.50);
      display:flex;
      gap: 10px;
      flex-wrap: wrap;
      align-items:center;
    }

    .dot{ opacity: 0.65; }

    .movie-cta{
      position:absolute;
      inset:0;
      display:grid;
      place-items:center;
      opacity:0;
      transition: opacity 160ms ease;
      pointer-events:none;
    }
    .card-wrap:hover .movie-cta{ opacity:1; }

    .movie-cta a{
      pointer-events:auto;
      padding: 10px 16px;
      border-radius: 999px;
      border: 1px solid rgba(255,255,255,0.20);
      background: rgba(10,10,16,0.45);
      backdrop-filter: blur(10px);
      -webkit-backdrop-filter: blur(10px);
      color: rgba(255,255,255,0.92) !important;
      font-weight: 800;
      letter-spacing: 0.2px;
      box-shadow: 0 18px 38px rgba(0,0,0,0.40);
      text-decoration: none !important;
      transform: translateY(0);
      transition: transform 160ms ease, background 160ms ease, border-color 160ms ease;
    }
    .movie-cta a:hover{
      transform: translateY(-1px);
      background: rgba(10,10,16,0.60);
      border-color: rgba(255,255,255,0.34);
    }

    div[data-testid="column"] > div{ gap: 0.35rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("📚 Catalogue des films")
st.caption("Filtre le catalogue. Résultats triés par Popularité ↓, Note ↓, Votes ↓. Affichage paginé par 24.")

CSV_PATH = OUTPUT_DIR / "10_final_imdb_tmdb.csv"
PAGE_SIZE = 24

POPULARITY_MAP = {
    "faible notoriété": 1,
    "peu populaire": 2,
    "populaire": 3,
    "très populaire": 4,
}


def split_csv_list(s: object) -> list[str]:
    if s is None or (isinstance(s, float) and np.isnan(s)):
        return []
    s = str(s).strip()
    if not s:
        return []
    return [normalize_txt(x, collapse_spaces=True) for x in s.split(",") if str(x).strip()]


def coerce_num(df: pd.DataFrame, col: str, default: float) -> None:
    if col not in df.columns:
        df[col] = default
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(default)


def rank_base(d: pd.DataFrame) -> pd.DataFrame:
    return d.sort_values(
        by=["_pop_score", "Note_moyenne", "Nombre_votes", "Titre"],
        ascending=[False, False, False, True],
        kind="mergesort",
    )


@st.cache_data(show_spinner=False)
def load_df(path: str) -> pd.DataFrame:
    return read_csv_clean_columns(path)


@st.cache_data(show_spinner=False)
def prepare_df(path: str) -> pd.DataFrame:
    df = load_df(path)

    for c in [
        "ID",
        "Titre",
        "Genre",
        "Réalisateurs",
        "Casting",
        "Pays_origine",
        "Poster1",
        "Poster2",
        "Accroche",
        "Résumé",
        "Popularité",
    ]:
        if c not in df.columns:
            df[c] = ""

    coerce_num(df, "Année_de_sortie", 0)
    df["Année_de_sortie"] = pd.to_numeric(df["Année_de_sortie"], errors="coerce").fillna(0).astype(int)

    coerce_num(df, "Note_moyenne", np.nan)
    coerce_num(df, "Nombre_votes", 0)

    df["_pop_score"] = df["Popularité"].astype(str).str.lower().map(POPULARITY_MAP).fillna(0).astype(int)

    df["_genre_list"] = df["Genre"].apply(split_csv_list)
    df["_dir_n"] = df["Réalisateurs"].fillna("").astype(str).map(lambda x: normalize_txt(x, collapse_spaces=True))
    df["_cast_n"] = df["Casting"].fillna("").astype(str).map(lambda x: normalize_txt(x, collapse_spaces=True))
    df["_country_n"] = df["Pays_origine"].fillna("").astype(str).map(lambda x: normalize_txt(x, collapse_spaces=True))

    df["_title_raw"] = df["Titre"].fillna("").astype(str).str.strip()
    df["_title_n"] = df["_title_raw"].map(lambda x: normalize_txt(x, collapse_spaces=True))

    return rank_base(df)


def _safe_text(x: object) -> str:
    s = "" if x is None else str(x)
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#039;")
    )


def _search_rank(df: pd.DataFrame, typed: str) -> pd.Series:
    q = normalize_txt(typed, collapse_spaces=True)
    if not q:
        return pd.Series(0, index=df.index, dtype="int64")

    t = df["_title_n"]

    exact = (t == q).astype("int64") * 1_000_000
    starts = t.str.startswith(q, na=False).astype("int64") * 100_000
    contains = t.str.contains(q, na=False).astype("int64") * 10_000

    n_tokens = max(1, len(q.split()))
    token_hits = pd.Series(0, index=df.index, dtype="int64")
    for tok in q.split():
        token_hits += t.str.contains(tok, na=False).astype("int64")
    token_score = (token_hits * (1000 // n_tokens)).astype("int64")

    return exact + starts + contains + token_score


df_ranked = prepare_df(str(CSV_PATH))

st.sidebar.header("Filtres")

all_genres = sorted({g for lst in df_ranked["_genre_list"] for g in lst if g})
genre_choice = st.sidebar.multiselect(
    "Genre",
    options=all_genres,
    default=[],
    help="Un film est gardé s'il contient au moins un des genres sélectionnés.",
    placeholder="Choisissez un ou plusieurs genres",
)

countries = sorted({x for x in df_ranked["_country_n"].unique().tolist() if x})
country_choice = st.sidebar.multiselect(
    "Origine (Pays)",
    options=countries,
    default=[],
    placeholder="Choisissez un pays d'origine",
)

director_query = st.sidebar.text_input("Réalisateur (contient)", placeholder="ex: Nolan")
actor_query = st.sidebar.text_input("Acteur / Actrice (contient)", placeholder="ex: Scarlett")

note_min = st.sidebar.slider("Note minimale", 0.0, 10.0, 0.0, 0.1)
year_min, year_max = st.sidebar.slider("Année de sortie", 1950, 2025, (1950, 2025), 1)

pop_choice = st.sidebar.selectbox(
    "Niveau de popularité minimum",
    options=["Tous", "Faible notoriété", "Peu populaire", "Populaire", "Très populaire"],
)

if st.sidebar.button("Réinitialiser les filtres"):
    for k in ["cat_page", "q_title"]:
        st.session_state.pop(k, None)
    st.rerun()

mask = pd.Series(True, index=df_ranked.index)

if genre_choice:
    chosen = [normalize_txt(g, collapse_spaces=True) for g in genre_choice]
    mask &= df_ranked["_genre_list"].apply(lambda lst: any(g in lst for g in chosen))

if country_choice:
    chosen_c = [normalize_txt(c, collapse_spaces=True) for c in country_choice]
    mask &= df_ranked["_country_n"].apply(lambda s: any(c in s for c in chosen_c))

if director_query.strip():
    q = normalize_txt(director_query, collapse_spaces=True)
    mask &= df_ranked["_dir_n"].str.contains(q, regex=False, na=False)

if actor_query.strip():
    q = normalize_txt(actor_query, collapse_spaces=True)
    mask &= df_ranked["_cast_n"].str.contains(q, regex=False, na=False)

if note_min > 0:
    mask &= df_ranked["Note_moyenne"].fillna(-1) >= float(note_min)

mask &= df_ranked["Année_de_sortie"].between(int(year_min), int(year_max), inclusive="both")

if pop_choice != "Tous":
    min_score = POPULARITY_MAP[pop_choice.lower()]
    mask &= df_ranked["_pop_score"] >= min_score

filtered = df_ranked.loc[mask]

st.markdown("### 🔎 Rechercher un film")

typed = st.text_input(
    "Recherche dans le titre",
    key="q_title",
    placeholder="Ex: avatar, seigneur, dark knight...",
).strip()

if typed:
    score = _search_rank(filtered, typed)
    qn = normalize_txt(typed, collapse_spaces=True)
    title_match = filtered["_title_n"].str.contains(qn, na=False) if qn else pd.Series(False, index=filtered.index)
    filtered = filtered.loc[title_match].copy()
    filtered["_q_score"] = score.loc[filtered.index]
    filtered = filtered.sort_values(
        by=["_q_score", "_pop_score", "Note_moyenne", "Nombre_votes", "Titre"],
        ascending=[False, False, False, False, True],
        kind="mergesort",
    )
else:
    filtered = filtered.sort_values(
        by=["_pop_score", "Note_moyenne", "Nombre_votes", "Titre"],
        ascending=[False, False, False, True],
        kind="mergesort",
    )

total = len(filtered)

st.session_state.setdefault("cat_page", 0)
max_pages = max(0, (total - 1) // PAGE_SIZE)
st.session_state.cat_page = min(st.session_state.cat_page, max_pages)

c1, c2, c3 = st.columns([1, 1, 3], vertical_alignment="center")
with c1:
    if st.button("⬅️ Précédent", disabled=st.session_state.cat_page == 0):
        st.session_state.cat_page -= 1
        st.rerun()
with c2:
    if st.button("Suivant ➡️", disabled=st.session_state.cat_page >= max_pages):
        st.session_state.cat_page += 1
        st.rerun()
with c3:
    if total == 0:
        st.caption("0 film(s)")
    else:
        start = st.session_state.cat_page * PAGE_SIZE
        end = min(start + PAGE_SIZE, total)
        st.caption(
            f"{total} film(s) — page {st.session_state.cat_page + 1} / {max_pages + 1} — affichage {start + 1} → {end}"
        )

if total == 0:
    st.warning("Aucun film ne correspond aux filtres.")
    st.stop()

start = st.session_state.cat_page * PAGE_SIZE
end = min(start + PAGE_SIZE, total)
page_df = filtered.iloc[start:end]


def render_grid(d: pd.DataFrame, n_cols: int = 6) -> None:
    rows = d.to_dict("records")

    for i in range(0, len(rows), n_cols):
        cols = st.columns(n_cols, vertical_alignment="top")

        for col, row in zip(cols, rows[i : i + n_cols]):
            with col:
                title = row.get("Titre", "—")
                year = row.get("Année_de_sortie", "—")
                rating = row.get("Note_moyenne", np.nan)
                votes = row.get("Nombre_votes", 0)

                poster_raw = row.get("Poster1", "") or row.get("Poster2", "")
                poster_url = resolve_poster_url(poster_raw)
                if not poster_url:
                    poster_url = "https://via.placeholder.com/500x750?text=No+Poster"

                t = _safe_text(title)
                y = _safe_text(year)
                r = f"{float(rating):.1f}" if pd.notna(rating) else "—"
                v = f"{int(votes):,}".replace(",", " ")

                href = f"Film_details?id={row['ID']}"

                st.markdown(
                    f"""
                    <div class="card-wrap">
                      <div class="movie-card" style="--poster:url('{poster_url}')">
                        <div class="movie-cta">
                          <a href="{href}">Voir la fiche</a>
                        </div>
                        <div class="movie-meta">
                          <div class="movie-title">{t}</div>
                          <div class="movie-sub">
                            <span>{y}</span>
                            <span class="dot">•</span>
                            <span>⭐ {r}</span>
                            <span class="dot">•</span>
                            <span>🗳️ {v}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


render_grid(page_df, n_cols=6)