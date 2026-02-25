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
    /* ===== Movie Card Wrapper ===== */
    .card-wrap{
      position: relative;
      border-radius: 18px;
      overflow: hidden;
      height: 390px;                 /* un peu plus haut pour éviter l’écrasement */
      box-shadow: 0 16px 40px rgba(0,0,0,0.35), inset 0 1px 0 rgba(255,255,255,0.06);
      border: 1px solid rgba(255,255,255,0.08);
    }

    /* Le poster: on l'affiche en ENTIER (contain) */
    .movie-card{
      position: relative;
      height: 100%;
      width: 100%;
      border-radius: 18px;
      overflow: hidden;
      background-image: var(--poster);
      background-repeat: no-repeat;
      background-size: contain;      /* <-- pour voir le poster en entier */
      background-position: center;
      background-color: rgba(0,0,0,0.25); /* fond quand le poster ne remplit pas tout */
      transform: translateZ(0);
      transition: transform 180ms ease, filter 180ms ease;
      filter: saturate(0.98) contrast(1.03);
    }

    .card-wrap:hover .movie-card{
      transform: scale(1.015);
      filter: saturate(1.05) contrast(1.07);
    }

    /* Dégradé global très léger */
    .movie-card::before{
      content:"";
      position:absolute;
      inset:0;
      background: radial-gradient(120% 120% at 50% 0%,
                rgba(255,255,255,0.08) 0%,
                rgba(0,0,0,0.20) 55%,
                rgba(0,0,0,0.55) 100%);
      pointer-events:none;
    }

    /* Bandeau bas (lecture titre/infos) */
    .movie-meta{
      position:absolute;
      left:0; right:0; bottom:0;
      padding: 14px 14px 12px 14px;
      background: linear-gradient(180deg,
                rgba(0,0,0,0.00) 0%,
                rgba(0,0,0,0.55) 35%,
                rgba(0,0,0,0.80) 100%);
      backdrop-filter: blur(10px);
      -webkit-backdrop-filter: blur(10px);
      pointer-events:none; /* ne bloque pas le clic du lien overlay */
    }

    .movie-title{
      font-size: 1.10rem;
      font-weight: 750;
      line-height: 1.15;
      margin: 0 0 6px 0;
      color: rgba(255,255,255,0.95);
      text-shadow: 0 6px 18px rgba(0,0,0,0.55);
    }

    .movie-sub{
      font-size: 0.92rem;
      font-weight: 600;
      color: rgba(255,255,255,0.78);
      margin: 0;
      text-shadow: 0 6px 18px rgba(0,0,0,0.50);
      display:flex;
      gap: 10px;
      flex-wrap: wrap;
      align-items:center;
    }

    .dot{ opacity: 0.65; }

    /* CTA hover (bouton visible au hover) */
    .movie-cta{
      position:absolute;
      inset:0;
      display:grid;
      place-items:center;
      opacity:0;
      transition: opacity 160ms ease;
      pointer-events:none; /* le lien <a> gère le clic */
    }
    .card-wrap:hover .movie-cta{ opacity:1; }

    /* le bouton hover est un <a> cliquable */
    .movie-cta a{
      pointer-events:auto;
      padding: 10px 16px;
      border-radius: 999px;
      border: 1px solid rgba(255,255,255,0.18);
      background: rgba(10,10,16,0.40);
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
      background: rgba(10,10,16,0.55);
      border-color: rgba(255,255,255,0.30);
    }

    /* Evite les gros gaps verticaux de Streamlit dans les colonnes */
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

    df["_pop_score"] = (
        df["Popularité"].astype(str).str.lower().map(POPULARITY_MAP).fillna(0).astype(int)
    )

    df["_genre_list"] = df["Genre"].apply(split_csv_list)
    df["_dir_n"] = df["Réalisateurs"].fillna("").astype(str).map(lambda x: normalize_txt(x, collapse_spaces=True))
    df["_cast_n"] = df["Casting"].fillna("").astype(str).map(lambda x: normalize_txt(x, collapse_spaces=True))
    df["_country_n"] = df["Pays_origine"].fillna("").astype(str).map(lambda x: normalize_txt(x, collapse_spaces=True))

    return rank_base(df)


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
        return title_index.iloc[0:0]
    keys = title_index["key"]
    starts = title_index[keys.str.startswith(q, na=False)]
    if len(starts) >= limit:
        return starts.head(limit)
    contains = title_index[keys.str.contains(q, na=False)]
    return pd.concat([starts, contains]).drop_duplicates("title").head(limit)


def _safe_text(x: object) -> str:
    s = "" if x is None else str(x)
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#039;")
    )


df_ranked = prepare_df(str(CSV_PATH))
title_index = build_title_index(df_ranked)


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
    for k in ["cat_page", "search_title", "search_suggestion"]:
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
    mask &= (df_ranked["Note_moyenne"].fillna(-1) >= float(note_min))

mask &= df_ranked["Année_de_sortie"].between(int(year_min), int(year_max), inclusive="both")

if pop_choice != "Tous":
    min_score = POPULARITY_MAP[pop_choice.lower()]
    mask &= (df_ranked["_pop_score"] >= min_score)

filtered = df_ranked.loc[mask]
total = len(filtered)

st.markdown("### 🔎 Rechercher un film")

typed = st.text_input(
    "Tape un titre (au moins 2 lettres)",
    key="search_title",
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
        key="search_suggestion",
    )

    if st.button("Ouvrir la fiche", type="primary"):
        st.session_state["go_to_title"] = chosen["title"]
        st.rerun()
else:
    if typed and len(typed) < 2:
        st.caption("Tape au moins 2 lettres.")

st.session_state.setdefault("cat_page", 0)
max_pages = max(0, (total - 1) // PAGE_SIZE)
st.session_state.cat_page = min(st.session_state.cat_page, max_pages)

c1, c2, c3 = st.columns([1, 1, 3], vertical_alignment="center")
with c1:
    if st.button("⬅️ Précédent", disabled=(st.session_state.cat_page == 0)):
        st.session_state.cat_page -= 1
        st.rerun()
with c2:
    if st.button("Suivant ➡️", disabled=(st.session_state.cat_page >= max_pages)):
        st.session_state.cat_page += 1
        st.rerun()
with c3:
    if total == 0:
        st.caption("0 film(s)")
    else:
        start = st.session_state.cat_page * PAGE_SIZE
        end = min(start + PAGE_SIZE, total)
        st.caption(f"{total} film(s) — page {st.session_state.cat_page + 1} / {max_pages + 1} — affichage {start + 1} → {end}")

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