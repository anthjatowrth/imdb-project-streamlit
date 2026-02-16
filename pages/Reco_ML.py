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
      <p style="margin:0;color:#A8A8C0;">Choisis un film, fixe des filtres, puis affiche les résultats par pages de 10.</p>
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


def title_exists(df: pd.DataFrame, title: str) -> bool:
    if not title:
        return False
    mask = df["Titre"].astype(str).str.strip().str.lower().eq(title.strip().lower())
    return bool(mask.any())



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
if "page" not in st.session_state:
    st.session_state.page = 0


def pick_title(title: str) -> None:
    """
    Called when user clicks a suggestion.
    We update 'typed_value' and bump 'typed_version' so the text_input is recreated
    with a new key and the selected title appears in the field.
    """
    st.session_state.selected_title = title
    st.session_state.typed_value = title
    st.session_state.typed_version += 1
    st.session_state.page = 0


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

    st.session_state.page = 0

    try:
        TOP_N = 200  

        reco_df = recommend(
            artifacts,
            title_query=title_query,
            year_min=int(year_min),
            year_max=int(year_max),
            min_rating=float(min_rating) if float(min_rating) > 0 else None,
            top_n=int(TOP_N),
            candidate_k=1200,
        )

        st.session_state.reco_df = reco_df

    except Exception as e:
        st.error(str(e))
        st.stop()



reco_df = st.session_state.reco_df

if reco_df is not None:
    page_size = 10
    total = len(reco_df)

    if total == 0:
        st.info("Aucun résultat avec ces filtres.")
        st.stop()

    max_pages = (total - 1) // page_size
    st.session_state.page = max(0, min(st.session_state.page, max_pages))

    start = st.session_state.page * page_size
    end = min(start + page_size, total)

    st.subheader("Résultats")
    st.write(f"{total} film(s) trouvé(s) — affichage {start+1} → {end}")

    b1, b2, b3 = st.columns([1, 1, 2], vertical_alignment="center")
    with b1:
        if st.button("⬅️ Précédent", disabled=(st.session_state.page == 0)):
            st.session_state.page -= 1
            st.rerun()

    with b2:
        if st.button("Suivant ➡️", disabled=(st.session_state.page >= max_pages)):
            st.session_state.page += 1
            st.rerun()

    with b3:
        st.caption(f"Page {st.session_state.page + 1} / {max_pages + 1}")

    st.dataframe(reco_df.iloc[start:end], use_container_width=True)

    with st.expander("Afficher tous les résultats"):
        st.dataframe(reco_df, use_container_width=True)