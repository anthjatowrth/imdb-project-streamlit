from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st

from src.ui import render_sidebar
from src.config import OUTPUT_DIR
from src.utils import load_css, normalize_txt, read_csv_clean_columns, pick_poster_url

st.set_page_config(page_title="Catalogue", layout="wide")

if "go_to_title" in st.session_state:
    _ = st.session_state.pop("go_to_title")
    st.switch_page("pages/Film_details.py")

load_css()
render_sidebar()

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
        "ID", "Titre", "Genre", "Réalisateurs", "Casting",
        "Pays_origine", "Poster1", "Poster2", "Accroche", "Résumé", "Popularité",
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


def render_pagination(current_page: int, max_pages: int, key_suffix: str) -> None:
    """Affiche la barre de pagination avec boutons gauche/droite et info centrale."""
    is_first = current_page == 0
    is_last = current_page >= max_pages

    st.markdown(
        f"""
        <div class="pagination-bar">
            <div class="pagination-info">
                Page {current_page + 1} / {max_pages + 1}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, center, right = st.columns([1, 4, 1])

    with left:
        if not is_first:
            if st.button("← Précédent", key=f"prev_{key_suffix}", use_container_width=True):
                st.session_state.cat_page -= 1
                st.rerun()

    with center:
        pass

    with right:
        if not is_last:
            if st.button("Suivant →", key=f"next_{key_suffix}", use_container_width=True):
                st.session_state.cat_page += 1
                st.rerun()


def render_grid(d: pd.DataFrame, n_cols: int = 6) -> None:
    rows = d.to_dict("records")

    for i in range(0, len(rows), n_cols):
        st.markdown('<div class="catalogue-grid-row">', unsafe_allow_html=True)
        cols = st.columns(n_cols, vertical_alignment="top")

        for col, row in zip(cols, rows[i : i + n_cols]):
            with col:
                title = row.get("Titre", "—")
                year = row.get("Année_de_sortie", "—")
                rating = row.get("Note_moyenne", np.nan)
                votes = row.get("Nombre_votes", 0)

                poster_url = pick_poster_url(pd.Series(row), cols=("Poster1", "Poster2"), imdb_col="ID")
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

        st.markdown('</div>', unsafe_allow_html=True)


# ── Filtres sidebar ───────────────────────────────────────────────────────────
df_ranked = prepare_df(str(CSV_PATH))

st.sidebar.header("Filtres")

all_genres = sorted({g for lst in df_ranked["_genre_list"] for g in lst if g})
genre_choice = st.sidebar.multiselect(
    "Genre", options=all_genres, default=[],
    help="Un film est gardé s'il contient au moins un des genres sélectionnés.",
    placeholder="Choisissez un ou plusieurs genres",
)

countries = sorted({x for x in df_ranked["_country_n"].unique().tolist() if x})
country_choice = st.sidebar.multiselect(
    "Origine (Pays)", options=countries, default=[],
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

# ── Filtrage ──────────────────────────────────────────────────────────────────
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

# ── Recherche par titre ───────────────────────────────────────────────────────
st.markdown("### 🔎 Rechercher un film")

typed = st.text_input(
    "Recherche dans le titre", key="q_title",
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

# ── Pagination ────────────────────────────────────────────────────────────────
total = len(filtered)

if total == 0:
    st.warning("Aucun film ne correspond aux filtres.")
    st.stop()

st.session_state.setdefault("cat_page", 0)
max_pages = max(0, (total - 1) // PAGE_SIZE)
st.session_state.cat_page = min(st.session_state.cat_page, max_pages)

start = st.session_state.cat_page * PAGE_SIZE
end = min(start + PAGE_SIZE, total)
page_df = filtered.iloc[start:end]

# Barre de pagination — haut
render_pagination(st.session_state.cat_page, max_pages, key_suffix="top")

st.divider()

# Grille de films
render_grid(page_df, n_cols=6)

st.divider()

# Barre de pagination — bas
render_pagination(st.session_state.cat_page, max_pages, key_suffix="bottom")
