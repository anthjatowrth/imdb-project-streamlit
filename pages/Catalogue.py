from __future__ import annotations

import re
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

from src.config import OUTPUT_DIR



st.set_page_config(page_title="Catalogue", layout="wide")


TMDB_IMG_BASE = "https://image.tmdb.org/t/p/w185"

def resolve_poster_url(poster: str) -> str | None:
    if not isinstance(poster, str):
        return None
    p = poster.strip()
    if not p:
        return None

 
    if p.startswith("http://") or p.startswith("https://"):
        return p


    if p.startswith("/") and (p.lower().endswith(".jpg") or p.lower().endswith(".png") or p.lower().endswith(".webp")):
        return TMDB_IMG_BASE + p


    from pathlib import Path
    if Path(p).exists():
        return p

    return None


def load_css() -> None:
    css_path = Path("assets/style.css")
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

load_css()


st.title("📚 Catalogue des films")
st.caption("Filtre le catalogue. Les résultats restent triés par Popularité ↓, Note ↓, Votes ↓. Affichage paginé par 20.")


def norm(s: str) -> str:
    s = "" if s is None else str(s)
    s = s.strip().lower()
    s = "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))
    s = re.sub(r"\s+", " ", s)
    return s


def split_csv_list(s: str) -> list[str]:
    """Pour Genre (souvent 'Action, Drama')"""
    if pd.isna(s) or str(s).strip() == "":
        return []
    return [norm(x) for x in str(s).split(",") if str(x).strip()]


def contains_any(haystack: pd.Series, needles: list[str]) -> pd.Series:
    """Recherche 'contient au moins un' en texte normalisé."""
    if not needles:
        return pd.Series(True, index=haystack.index)
    h = haystack.fillna("").astype(str).map(norm)
    pattern = "|".join(re.escape(n) for n in needles)
    return h.str.contains(pattern, regex=True, na=False)


@st.cache_data(show_spinner=False)
def load_df(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, sep=",")
    df.columns = df.columns.str.strip()
    return df


def coerce_num(df: pd.DataFrame, col: str, default: float = 0.0) -> None:
    if col not in df.columns:
        df[col] = default
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(default)



df = load_df(str(OUTPUT_DIR / "10_final_imdb_tmdb.csv"))


coerce_num(df, "Année_de_sortie", 0)
df["Année_de_sortie"] = df["Année_de_sortie"].astype(int, errors="ignore")

coerce_num(df, "Note_moyenne", np.nan)
coerce_num(df, "Nombre_votes", 0)
coerce_num(df, "Popularité", 0)


for c in ["Titre", "Genre", "Réalisateurs", "Casting", "Pays_origine", "Poster1", "Accroche", "Résumé"]:
    if c not in df.columns:
        df[c] = ""


df["_genre_list"] = df["Genre"].apply(split_csv_list)
df["_titre_n"] = df["Titre"].map(norm)
df["_dir_n"] = df["Réalisateurs"].fillna("").astype(str).map(norm)
df["_cast_n"] = df["Casting"].fillna("").astype(str).map(norm)
df["_country_n"] = df["Pays_origine"].fillna("").astype(str).map(norm)

POPULARITY_MAP = {
    "faible notoriété": 1,
    "peu populaire": 2,
    "populaire": 3,
    "très populaire": 4,
}

df["_pop_score"] = (
    df["Popularité"]
    .astype(str)
    .str.lower()
    .map(POPULARITY_MAP)
    .fillna(0)
)

def rank_base(d: pd.DataFrame) -> pd.DataFrame:
    # tri stable : popularité, note, votes
    return d.sort_values(
        by=["Popularité", "Note_moyenne", "Nombre_votes", "Titre"],
        ascending=[False, False, False, True],
        kind="mergesort",
    )


df_ranked = rank_base(df)



st.sidebar.header("Filtres")


all_genres = sorted({g for lst in df["_genre_list"] for g in lst if g})
genre_choice = st.sidebar.multiselect(
    "Genre",
    options=all_genres,
    default=[],
    help="Un film est gardé s'il contient au moins un des genres sélectionnés.",
)


countries = sorted({x for x in df["_country_n"].unique().tolist() if x})
country_choice = st.sidebar.multiselect(
    "Origine (Pays)",
    options=countries,
    default=[],
)

director_query = st.sidebar.text_input("Réalisateur (contient)", placeholder="ex: nolan")
actor_query = st.sidebar.text_input("Acteur / Actrice (contient)", placeholder="ex: scarlett")

note_min = st.sidebar.slider("Note minimale", min_value=0.0, max_value=10.0, value=0.0, step=0.1)

year_min, year_max = st.sidebar.slider(
    "Année de sortie",
    min_value=1950,
    max_value=2025,
    value=(1950, 2025),
    step=1,
)

pop_choice = st.sidebar.selectbox(
    "Niveau de popularité minimum",
    options=[
        "Tous",
        "Faible notoriété",
        "Peu populaire",
        "Populaire",
        "Très populaire",
    ],
)


if st.sidebar.button("Réinitialiser les filtres"):
    st.session_state.clear()
    st.rerun()


mask = pd.Series(True, index=df_ranked.index)


if genre_choice:
    chosen = [norm(g) for g in genre_choice]
    mask = mask & df_ranked["_genre_list"].apply(lambda lst: any(g in lst for g in chosen))


if country_choice:
    chosen_c = [norm(c) for c in country_choice]
    mask = mask & contains_any(df_ranked["Pays_origine"], chosen_c)


if director_query.strip():
    q = norm(director_query)
    mask = mask & df_ranked["_dir_n"].str.contains(re.escape(q), regex=True, na=False)


if actor_query.strip():
    q = norm(actor_query)
    mask = mask & df_ranked["_cast_n"].str.contains(re.escape(q), regex=True, na=False)


if note_min > 0:
    mask = mask & (df_ranked["Note_moyenne"].fillna(-1) >= float(note_min))


mask = mask & df_ranked["Année_de_sortie"].between(int(year_min), int(year_max), inclusive="both")


if pop_choice != "Tous":
    min_score = POPULARITY_MAP[pop_choice.lower()]
    mask = mask & (df_ranked["_pop_score"] >= min_score)

filtered = df_ranked.loc[mask].copy()
filtered = rank_base(filtered)  



PAGE_SIZE = 20
if "cat_page" not in st.session_state:
    st.session_state.cat_page = 0

total = len(filtered)
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
    start = st.session_state.cat_page * PAGE_SIZE
    end = min(start + PAGE_SIZE, total)
    st.caption(f"{total} film(s) — page {st.session_state.cat_page + 1} / {max_pages + 1} — affichage {start + 1} → {end}")


page_df = filtered.iloc[start:end].copy()



def render_card(row: pd.Series) -> None:
    title = row.get("Titre", "")
    year = row.get("Année_de_sortie", "")
    rating = row.get("Note_moyenne", np.nan)
    votes = row.get("Nombre_votes", 0)
    pop = row.get("Popularité", 0)
    genre = row.get("Genre", "")
    directors = row.get("Réalisateurs", "")
    cast = row.get("Casting", "")
    country = row.get("Pays_origine", "")
    poster = row.get("Poster1", "") or row.get("Poster2", "")
    tagline = row.get("Accroche", "")
    summary = row.get("Résumé", "")

    left, right = st.columns([1, 3], vertical_alignment="top")
    with left:
        if isinstance(poster, str) and poster.strip():
            poster_raw = row.get("Poster1", "") or row.get("Poster2", "")
            poster_url = resolve_poster_url(poster_raw)

            with left:
                if poster_url:
                    st.image(poster_url, use_container_width=120)
                else:
                    st.write("🖼️ (pas d'affiche)")
        else:
            st.write("🖼️ (pas d'affiche)")

    with right:
        st.markdown(f"### {title} ({year})")
        st.write(
            f"⭐ **{rating if pd.notna(rating) else '—'}**  "
            f"· 🗳️ **{int(votes):,}** votes  "
            f"· 🔥 Popularité **{pop}**"
        )
        if genre:
            st.write(f"**Genre :** {genre}")
        if country:
            st.write(f"**Origine :** {country}")
        if directors:
            st.write(f"**Réalisateurs :** {directors}")
        if cast:
            st.write(f"**Casting :** {cast}")

        if isinstance(tagline, str) and tagline.strip():
            st.info(tagline)

        if isinstance(summary, str) and summary.strip():
            with st.expander("Résumé"):
                st.write(summary)

    st.divider()


# -------------------------
# Display as GRID (4 cols x 5 rows)
# -------------------------
def render_grid(page_df: pd.DataFrame, n_cols: int = 4) -> None:
    rows = page_df.to_dict("records")

    for i in range(0, len(rows), n_cols):
        cols = st.columns(n_cols, vertical_alignment="top")
        chunk = rows[i:i + n_cols]

        for col, row in zip(cols, chunk):
            with col:
                title = row.get("Titre", "")
                year = row.get("Année_de_sortie", "")
                rating = row.get("Note_moyenne", None)
                votes = row.get("Nombre_votes", 0)
                pop = row.get("Popularité", 0)
                genre = row.get("Genre", "")
                directors = row.get("Réalisateurs", "")
                country = row.get("Pays_origine", "")
                poster_raw = row.get("Poster1", "") or row.get("Poster2", "")
                tagline = row.get("Accroche", "")
                summary = row.get("Résumé", "")

                poster_url = resolve_poster_url(poster_raw)

                # --- Card container
                with st.container(border=120):
                    if poster_url:
                        st.image(poster_url, use_container_width=120)
                    else:
                        st.write("🖼️ (pas d'affiche)")

                    st.markdown(f"**{title}**")
                    st.caption(f"{year} · ⭐ {rating if pd.notna(rating) else '—'} · 🗳️ {int(votes):,} · 🔥 {pop}")

                    # petites infos (optionnel)
                    if genre:
                        st.write(f"**Genre :** {genre}")
                    if country:
                        st.write(f"**Origine :** {country}")
                    if directors:
                        st.write(f"**Réalisateur :** {directors}")

                    # tagline / résumé en repli
                    if isinstance(tagline, str) and tagline.strip():
                        st.caption(f"“{tagline}”")

                    if isinstance(summary, str) and summary.strip():
                        with st.expander("Résumé"):
                            st.write(summary)


if total == 0:
    st.warning("Aucun film ne correspond aux filtres.")
else:
    render_grid(page_df, n_cols=4)

# Optionnel : afficher brut en dataframe
with st.expander("Voir le tableau (debug)"):
    show_cols = [
        "ID", "Titre", "Année_de_sortie", "Genre", "Note_moyenne",
        "Nombre_votes", "Popularité", "Réalisateurs", "Casting", "Pays_origine"
    ]
    show_cols = [c for c in show_cols if c in filtered.columns]
    st.dataframe(filtered[show_cols].iloc[start:end], use_container_width=True)