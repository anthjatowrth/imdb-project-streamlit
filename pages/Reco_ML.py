from __future__ import annotations

import unicodedata
from pathlib import Path

import pandas as pd
import streamlit as st

from src.config import OUTPUT_DIR
from src.reco.engine import build_artifacts, recommend

st.set_page_config(page_title="Recommandations", layout="wide")



def load_css() -> None:
    css_path = Path("assets/style.css")
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


load_css()

st.markdown(
    """
    <div style="
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 18px;
        padding: 18px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.35);
        margin-bottom: 14px;
    ">
      <h3 style="margin:0 0 8px 0;">🎬 Recommandations</h3>
      <p style="margin:0;color:#A8A8C0;">Choisis un film, fixe des filtres, puis affiche 3 recommandations par catégorie de popularité.</p>
    </div>
    """,
    unsafe_allow_html=True,
)



def normalize_txt(s: str) -> str:
    s = "" if s is None else str(s)
    s = s.strip().lower()
    s = "".join(
        c for c in unicodedata.normalize("NFKD", s)
        if not unicodedata.combining(c)
    )
    return s


TMDB_IMG_BASE = "https://image.tmdb.org/t/p/w500"  

def to_poster_url(raw: str | None) -> str | None:
    if raw is None:
        return None
    s = str(raw).strip()
    if not s or s.lower() == "nan":
        return None

    if s.startswith("http://") or s.startswith("https://"):
        return s

    if s.startswith("/"):
        return TMDB_IMG_BASE + s

    if s.startswith("//"):
        return "https:" + s

    return None


def pick_poster_url(row: pd.Series) -> str | None:
    for col in ("Poster1", "Poster2"):
        if col in row and pd.notna(row[col]):
            url = to_poster_url(row[col])
            if url:
                return url
    return None


def title_exists(df: pd.DataFrame, title: str) -> bool:
    if not title:
        return False
    mask = df["Titre"].astype(str).str.strip().str.lower().eq(title.strip().lower())
    return bool(mask.any())


@st.cache_data(show_spinner=False)
def load_df(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, sep=",")
    df.columns = df.columns.str.strip()
    return df


@st.cache_resource(show_spinner=True)
def load_artifacts(df: pd.DataFrame) -> dict:
    return build_artifacts(df)


@st.cache_data(show_spinner=False)
def build_title_index(df: pd.DataFrame) -> pd.DataFrame:
    titles = df["Titre"].dropna().astype(str).str.strip()
    idx = pd.DataFrame({"title": titles})
    idx["key"] = idx["title"].map(normalize_txt)
    return idx.drop_duplicates("title").reset_index(drop=True)


def get_suggestions(title_index: pd.DataFrame, typed: str, limit: int = 12) -> list[str]:
    q = normalize_txt(typed)
    if len(q) < 2:
        return []

    starts = title_index[title_index["key"].str.startswith(q)]
    if len(starts) >= limit:
        sug = starts.head(limit)
    else:
        contains = title_index[title_index["key"].str.contains(q, na=False)]
        sug = pd.concat([starts, contains]).drop_duplicates("title").head(limit)

    return sug["title"].tolist()


def get_forced_3x3_recos(
    artifacts: dict,
    *,
    title_query: str,
    year_min: int,
    year_max: int,
    min_rating: float | None,
    base_top_n: int = 600,
    candidate_k_start: int = 1200,
    candidate_k_max: int = 8000,
    step_factor: float = 1.8,
) -> pd.DataFrame:
    """
    Objectif: obtenir jusqu'à 3 films par catégorie de popularité (3 catégories).
    Stratégie:
    - appeler recommend() avec candidate_k croissant jusqu'à remplir les catégories ou atteindre la limite.
    - dans chaque appel, on prend un pool assez large (top_n=base_top_n) puis on sélectionne 3 par catégorie.
    """
    target_order = ["Très populaire", "Populaire", "Peu populaire"]
    candidate_k = int(candidate_k_start)

    best = None

    while candidate_k <= candidate_k_max:
        reco_df = recommend(
            artifacts,
            title_query=title_query,
            year_min=int(year_min),
            year_max=int(year_max),
            min_rating=min_rating,
            top_n=int(base_top_n),       
            candidate_k=int(candidate_k), 
        )

        if "Popularité" not in reco_df.columns:
            raise ValueError("La colonne 'Popularité' est absente des résultats de recommend().")

        tmp = reco_df[reco_df["Popularité"].isin(target_order)].copy()

        if "distance_cosine" in tmp.columns:
            tmp = tmp.sort_values("distance_cosine", ascending=True)

        selected = tmp.groupby("Popularité", sort=False).head(2)

     
        counts = selected["Popularité"].value_counts()
        complete = all(int(counts.get(cat, 0)) >= 2 for cat in target_order)

        best = selected  

        if complete:
            break

        candidate_k = int(candidate_k * step_factor)

 
    best = best.copy()
    best["__cat_order"] = best["Popularité"].map(
        {"Très populaire": 0, "Populaire": 1, "Peu populaire": 2}
    ).fillna(99).astype(int)

    if "distance_cosine" in best.columns:
        best = best.sort_values(["__cat_order", "distance_cosine"], ascending=[True, True])
    else:
        best = best.sort_values(["__cat_order"], ascending=True)

    return best.drop(columns=["__cat_order"])


df_raw = load_df(str(OUTPUT_DIR / "10_final_imdb_tmdb.csv"))
artifacts = load_artifacts(df_raw)
df2 = artifacts["df"]
title_index = build_title_index(df2)


if "selected_title" not in st.session_state:
    st.session_state.selected_title = ""
if "typed_version" not in st.session_state:
    st.session_state.typed_version = 0
if "typed_value" not in st.session_state:
    st.session_state.typed_value = ""
if "reco_df" not in st.session_state:
    st.session_state.reco_df = None


def pick_title(title: str) -> None:
    st.session_state.selected_title = title
    st.session_state.typed_value = title
    st.session_state.typed_version += 1



col1, col2, col3 = st.columns([2.2, 1.2, 1.2], vertical_alignment="top")

with col1:
    typed_key = f"typed_title_{st.session_state.typed_version}"
    st.text_input(
        "Film de référence (titre)",
        key=typed_key,
        value=st.session_state.typed_value,
        placeholder="Ex: Avatar",
    )

    typed = st.session_state.get(typed_key, "").strip()
    suggestions = get_suggestions(title_index, typed, limit=12)

    if suggestions:
        st.caption("Suggestions (clique pour sélectionner le bon titre) :")
        for t in suggestions:
            st.button(t, key=f"sug_{t}", on_click=pick_title, args=(t,))

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
    title_query = (st.session_state.selected_title or "").strip()

    if not title_query:
        st.warning("Clique une suggestion pour sélectionner un film exact avant de lancer.")
        st.stop()

    if not title_exists(df2, title_query):
        st.warning("Le film sélectionné n'existe pas dans la base (essaie via les suggestions).")
        st.stop()

    try:
        reco_3x3 = get_forced_3x3_recos(
            artifacts,
            title_query=title_query,
            year_min=int(year_min),
            year_max=int(year_max),
            min_rating=float(min_rating) if float(min_rating) > 0 else None,
            base_top_n=600,
            candidate_k_start=1200,
            candidate_k_max=8000,
        )

        st.session_state.reco_df = reco_3x3

    except Exception as e:
        st.error(str(e))
        st.stop()


reco_df = st.session_state.reco_df

if reco_df is not None:
    target_order = ["Très populaire", "Populaire", "Peu populaire"]

    st.subheader("Recommandations (3 par catégorie de popularité)")

    c1, c2, c3 = st.columns(3, vertical_alignment="top")
    col_map = {"Très populaire": c1, "Populaire": c2, "Peu populaire": c3}

    for cat in target_order:
        with col_map[cat]:
            st.markdown(f"### {cat}")

            block = reco_df[reco_df["Popularité"] == cat].head(3)

      
            if len(block) < 2:
                st.caption(f"⚠️ {len(block)}/3 trouvés (après filtres).")

            if block.empty:
                st.caption("Aucun résultat.")
                continue

            for _, row in block.iterrows():
                poster_url = pick_poster_url(row)

                with st.container(border=True):
                    if poster_url:
                        st.image(poster_url, use_container_width=True)
                    else:
                        st.caption("Poster indisponible")

                    title = row["Titre"]
                    st.page_link("pages/Film_details.py", label="Voir la fiche", query_params={"title": title})
                    year = row.get("Année_de_sortie", "—")
                    rating = row.get("Note_moyenne", "—")
                    dist = row.get("distance_cosine", "—")
                    
                    
                    st.markdown(f"**{title}**")
                    st.caption(f"Année: {year} • Note: {rating} • Distance cosine: {dist}")

                    if "Genre" in row and pd.notna(row["Genre"]):
                        st.caption(f"Genre: {row['Genre']}")
                    if "Réalisateurs" in row and pd.notna(row["Réalisateurs"]):
                        st.caption(f"Réal: {row['Réalisateurs']}")

    with st.expander("Afficher les 9 résultats (table)"):
        st.dataframe(reco_df, use_container_width=True)
