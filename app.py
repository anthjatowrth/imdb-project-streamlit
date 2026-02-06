from __future__ import annotations
import streamlit as st

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(
    page_title="IMDb Recommender",
    page_icon="🎬",
    layout="wide",
)

# -----------------------------
# Helpers
# -----------------------------
def clean_text(s: str) -> str:
    return " ".join(s.strip().split())

# -----------------------------
# Header
# -----------------------------
col_logo, col_title = st.columns([1, 6])
with col_logo:
    # Tu peux remplacer par ton logo local : st.image("assets/logo.png", width=90)
    st.markdown("## 🎬")
with col_title:
    st.title("IMDb Recommender")
    st.caption(
        "Une app Streamlit pour recommander des films en fonction de tes préférences "
        "(années, genres, réalisateur, film favori…)."
    )

st.divider()

# -----------------------------
# Layout: sidebar for inputs
# -----------------------------
with st.sidebar:
    st.header("🎛️ Tes préférences")

    # Range d'années (1950-2025)
    year_min, year_max = st.slider(
        "Période",
        min_value=1950,
        max_value=2025,
        value=(1990, 2020),
        step=1,
        help="Choisis une plage d'années de sortie.",
    )

    # Champs texte (tu pourras remplacer par selectbox quand tu auras la liste depuis ton dataset)
    fav_director = st.text_input("Réalisateur préféré", placeholder="Ex: Christopher Nolan")
    fav_movie = st.text_input("Film préféré", placeholder="Ex: Inception")

    # Genres (liste exemple — à remplacer par df['genres'].unique() quand tu brancheras les données)
    genres_options = [
        "Action", "Adventure", "Animation", "Comedy", "Crime", "Drama",
        "Fantasy", "Horror", "Mystery", "Romance", "Sci-Fi", "Thriller",
    ]
    fav_genres = st.multiselect(
        "Genres préférés",
        options=genres_options,
        default=["Drama", "Thriller"],
    )

    # Curseur “profil” (optionnel)
    min_rating = st.slider("Note minimale (optionnel)", 0.0, 10.0, 7.0, 0.1)
    min_votes = st.number_input("Votes minimum (optionnel)", min_value=0, value=5000, step=500)

    st.divider()

    go = st.button("✨ Obtenir des recommandations", use_container_width=True)

# -----------------------------
# Main content
# -----------------------------
left, right = st.columns([3, 2], vertical_alignment="top")

with left:
    st.subheader("📌 À propos du projet")
    st.write(
        "Cette application te propose des recommandations à partir d'une base IMDb enrichie "
        "(notes, votes, genres, années, réalisateur, casting…). "
        "L’idée : tu renseignes quelques préférences, et on te renvoie une sélection cohérente."
    )

    st.markdown("### 🧭 Comment ça marche (version simple)")
    st.markdown(
        "- Tu choisis une période (1950–2025)\n"
        "- Tu indiques tes genres préférés\n"
        "- Optionnel : ton réalisateur / film préféré\n"
        "- On filtre + on score les films proches de ton profil\n"
        "- On te propose une shortlist avec affiches et infos"
    )

    st.info(
        "À ce stade, c’est un écran d’accueil + formulaire. "
        "La logique de recommandation sera branchée ensuite sur ton dataset final.",
        icon="ℹ️",
    )

with right:
    st.subheader("🎞️ Aperçu d’affiches (démo)")
    st.caption("Pour l’instant, ce sont des affiches d’exemple (URLs publiques).")

    # ⚠️ Ces images sont là comme “placeholder”.
    # Quand tu auras des URLs d’affiches dans ta base (ou via TMDB),
    # tu remplaceras simplement cette liste.
    posters = [
        "https://upload.wikimedia.org/wikipedia/en/7/7e/Inception_ver3.jpg",
        "https://upload.wikimedia.org/wikipedia/en/8/8a/Dark_Knight.jpg",
        "https://upload.wikimedia.org/wikipedia/en/2/2e/Interstellar_film_poster.jpg",
        "https://upload.wikimedia.org/wikipedia/en/9/9a/Forrest_Gump_poster.jpg",
    ]

    pcol1, pcol2 = st.columns(2)
    with pcol1:
        st.image(posters[0], use_container_width=True)
        st.image(posters[2], use_container_width=True)
    with pcol2:
        st.image(posters[1], use_container_width=True)
        st.image(posters[3], use_container_width=True)

st.divider()

# -----------------------------
# Debug / Preview of selections
# -----------------------------
st.subheader("🧾 Récapitulatif de tes choix")
summary = {
    "Années": f"{year_min} – {year_max}",
    "Genres": ", ".join(fav_genres) if fav_genres else "(aucun)",
    "Réalisateur préféré": clean_text(fav_director) if fav_director else "(non renseigné)",
    "Film préféré": clean_text(fav_movie) if fav_movie else "(non renseigné)",
    "Note minimale": min_rating,
    "Votes minimum": int(min_votes),
}
st.json(summary)

# -----------------------------
# Call-to-action
# -----------------------------
if go:
    st.success("✅ OK ! (Prochaine étape) Ici, on branchera le moteur de recommandation.", icon="✅")
    st.markdown(
        "👉 À implémenter ensuite :\n"
        "- Charger ton dataset final (parquet/csv)\n"
        "- Normaliser genres / années\n"
        "- Filtrer selon tes préférences\n"
        "- Scorer (content-based ou hybride)\n"
        "- Afficher un Top N avec affiches + détails")