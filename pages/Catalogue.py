from __future__ import annotations
from src.ui import render_sidebar
import numpy as np
import pandas as pd
import streamlit as st

from src.config import OUTPUT_DIR
from src.utils import load_css, normalize_txt, read_csv_clean_columns, resolve_poster_url, format_votes, format_duration, format_countries_fr

st.set_page_config(page_title="Catalogue", layout="wide")

if "go_to_title" in st.session_state:
    title = st.session_state.pop("go_to_title")
    st.switch_page("pages/Film_details.py")

load_css()
render_sidebar()

st.title("📚 Catalogue des films")
st.caption("Filtre le catalogue. Résultats triés par Popularité ↓, Note ↓, Votes ↓. Affichage paginé par 20.")

CSV_PATH = OUTPUT_DIR / "10_final_imdb_tmdb.csv"
PAGE_SIZE = 30

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

    for c in ["Titre", "Genre", "Réalisateurs", "Casting", "Pays_origine", "Poster1", "Poster2", "Accroche", "Résumé", "Popularité"]:
        if c not in df.columns:
            df[c] = ""

    coerce_num(df, "Année_de_sortie", 0)
    df["Année_de_sortie"] = df["Année_de_sortie"].astype(int, errors="ignore")
    coerce_num(df, "Note_moyenne", np.nan)
    coerce_num(df, "Nombre_votes", 0)

    df["_pop_score"] = (
        df["Popularité"]
        .astype(str)
        .str.lower()
        .map(POPULARITY_MAP)
        .fillna(0)
        .astype(int)
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

df_ranked = prepare_df(str(CSV_PATH))
title_index = build_title_index(df_ranked)

st.sidebar.header("Filtres")

all_genres = sorted({g for lst in df_ranked["_genre_list"] for g in lst if g})
genre_choice = st.sidebar.multiselect(
    "Genre",
    options=all_genres,
    default=[],
    help="Un film est gardé s'il contient au moins un des genres sélectionnés.",
)

countries = sorted({x for x in df_ranked["_country_n"].unique().tolist() if x})
country_choice = st.sidebar.multiselect("Origine (Pays)", options=countries, default=[])

director_query = st.sidebar.text_input("Réalisateur (contient)", placeholder="ex: nolan")
actor_query = st.sidebar.text_input("Acteur / Actrice (contient)", placeholder="ex: scarlett")

note_min = st.sidebar.slider("Note minimale", 0.0, 10.0, 0.0, 0.1)
year_min, year_max = st.sidebar.slider("Année de sortie", 1950, 2025, (1950, 2025), 1)

pop_choice = st.sidebar.selectbox(
    "Niveau de popularité minimum",
    options=["Tous", "Faible notoriété", "Peu populaire", "Populaire", "Très populaire"],
)

if st.sidebar.button("Réinitialiser les filtres"):
    for k in ["cat_page"]:
        st.session_state.pop(k, None)
    st.rerun()

mask = pd.Series(True, index=df_ranked.index)

if genre_choice:
    chosen = [normalize_txt(g, collapse_spaces=True) for g in genre_choice]
    mask &= df_ranked["_genre_list"].apply(lambda lst: any(g in lst for g in chosen))

    sug_df = get_suggestions(title_index, typed, limit=10)

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

st.session_state.setdefault("cat_page", 0)
max_pages = max(0, (total - 1) // PAGE_SIZE)
st.session_state.cat_page = min(st.session_state.cat_page, max_pages)

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

def render_grid(d: pd.DataFrame, n_cols: int = 4) -> None:
    rows = d.to_dict("records")
    for i in range(0, len(rows), n_cols):
        cols = st.columns(n_cols, vertical_alignment="top")
        for col, row in zip(cols, rows[i : i + n_cols]):
            with col:
                title = row.get("Titre", "—")
                year = row.get("Année_de_sortie", "—")
                rating = row.get("Note_moyenne", np.nan)
                votes = row.get("Nombre_votes", 0)
                pop_label = row.get("Popularité", "")
                genre = row.get("Genre", "")
                directors = row.get("Réalisateurs", "")
                country = row.get("Pays_origine", "")
                tagline = row.get("Accroche", "")

                poster_raw = row.get("Poster1", "") or row.get("Poster2", "")
                poster_url = resolve_poster_url(poster_raw)

                with st.container(border=True):
                    if poster_url:
                        st.image(poster_url, use_container_width=True, output_format="JPEG", caption=None)
                        st.markdown(
                            """
                            <style>
                            [data-testid="stImage"] img{
                                height: 220px;
                                object-fit: cover;
                                width: 100%;
                                border-radius: 6px;
                            }
                            </style>
                            """,
                            unsafe_allow_html=True,)
                    else:
                        st.caption("🖼️ (pas d'affiche)")

                    votes_txt = format_votes(votes)
                    rating_txt = f"{rating:.1f}" if pd.notna(rating) else "—"
                    year_txt = str(int(year)) if pd.notna(year) and str(year).strip() != "" else "—"
                    pop_txt = pop_label if str(pop_label).strip() else "—"

                    st.markdown(
                        f"""
                        <div style='font-size:16px;font-weight:600;height:40px;white-space:nowrap;overflow:hidden;text-align:center;text-overflow:ellipsis'>{title}</div>
                        <div style="font-size:13px;opacity:0.75;line-height:1.5;margin-top:6px;text-align:center;">
                                {year_txt}<br>
                            ⭐ {rating_txt}<br>
                            🗳️ {votes_txt}<br>
                            🔥 {pop_txt}
                        </div>
                        """,
                        unsafe_allow_html=True)

                    if genre:
                        st.caption(f"Genre : {genre}")
                    if country:
                        st.caption(f"Origine : {country}")
                    if directors:
                        st.caption(f"Réalisateur : {directors}")

                    if isinstance(tagline, str) and tagline.strip():
                        st.caption(f"“{tagline}”")

                    st.page_link(
                        "pages/Film_details.py",
                        label="Voir la fiche",
                        query_params={"title": title},
                    )

render_grid(page_df, n_cols=6)
