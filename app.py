import streamlit as st
from src.ui import render_sidebar
from src.utils import load_css, pick_poster_url
st.set_page_config(
    page_title="CinéData Creuse — TetraData",
    page_icon="🎬",
    layout="wide",
)
load_css()
render_sidebar()

st.markdown(
    """
<div style="text-align:center; margin: 0.2rem 0 1.5rem 0;">
  <div style="
      font-family:'Bebas Neue', Impact, sans-serif;
      font-size: clamp(3rem, 5vw, 5rem);
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: #FFD700;
      filter: drop-shadow(0 0 12px rgba(255,200,0,0.5)) drop-shadow(0 0 35px rgba(255,180,0,0.3));
  ">
    Bienvenue sur CinéData
  </div>
  <div style="
      color: rgba(210,210,235,0.9);
      font-size: 1.15rem;
      margin-top: 0.3rem;
      letter-spacing: 0.04em;
  ">
    Explore, découvre et trouve ton prochain chef-d'œuvre.
  </div>
  <div style="
      width: 120px;
      height: 3px;
      margin: 20px auto 0;
      background: linear-gradient(90deg, transparent, #7b68ee, transparent);
      box-shadow: 0 0 15px rgba(123,104,238,0.6);
  "></div>
</div>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------
# HERO (base)
# ---------------------------------------------------------------------


st.caption("🎥 Cinéma indépendant · Département 23")

st.write("**La data au service du cinéma de proximité.**")

st.write(
    "CinéData Creuse naît de la rencontre entre un cinéma indépendant de la Creuse "
    "et la puissance de l'analyse de données. Moderniser sans perdre l'âme locale — "
    "c'est notre mission chez TetraData."
)



st.divider()

st.markdown("""
<style>
button[data-baseweb="tab"] {
    font-size: 1.2rem;
    padding: 1rem 2.5rem;
    letter-spacing: 0.08em;
}
div[data-testid="stTabs"] > div:first-child {
    justify-content: center;
}
</style>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["Notre Projet", "La Creuse", "TetraData"])

with tab1 :

    st.header("Le projet & l'organisation")
    st.caption("TetraData")

    flux = st.columns(5, gap="small")
    items = [
        ("🎬", "Client", "Cinéma indépendant local", "Acteur culturel essentiel de la Creuse"),
        ("📉", "Constat", "Baisse de fréquentation", "Concurrence croissante des plateformes de streaming"),
        ("🎯", "Besoin", "Mieux comprendre", "Comprendre les spectateurs et adapter l'offre"),
        ("💡", "Solution", "Analyse de données", "Moteur de recommandation personnalisée"),
        ("📦", "Livrables", "Application + Dashboard", "Appli spectateur + tableau de bord décisionnel"),
    ]
    for col, (ico, label, title, desc) in zip(flux, items):
        with col:
            st.write(f"### {ico} {label}")
            st.write(f"**{title}**")
            st.caption(desc)

    st.write("")
    c1, c2 = st.columns(2, gap="large")

    with c1:
        st.subheader("TetraData — Notre histoire")
        st.write(
            "TetraData est née de la rencontre de plusieurs experts en data, unis par la passion "
            "de transformer les données en décisions stratégiques pour des clients dans divers secteurs."
        )
        st.write(
            "Notre mission : aider les structures locales à mieux comprendre leur public et à prendre "
            "des décisions éclairées grâce à des outils simples, accessibles et adaptés."
        )

    with c2:
        st.subheader("Nos outils & technologies")
        outils = ["Python", "Streamlit", "GitHub", "VS Code", "Google Drive", "Discord", "Excel", "Power BI"]
        st.write(", ".join(outils))

    
with tab3:
    col1, col2, col3 = st.columns(3, gap="large")
    with col1:
        st.image("assets/logo_blanc_DT.png")
    with col2:
        st.markdown("""
        **TetraData** est née de la rencontre de plusieurs experts en data, unis par la passion
        de transformer les données en décisions stratégiques pour des clients dans divers secteurs d'activité.

        Des entreprises comme **Coca-Cola, Netflix, Leboncoin, Air France** et **Peugeot** nous ont fait confiance.
        Nous sommes engagés autour de certifications reconnues : Lean 6 Sigma, label RSE et Great Place to Work.

        Notre équipe travaille selon la **méthode Agile** : à partir d'un Backlog Produit, nous planifions des sprints
        rythmés par des réunions d'équipe, des revues de sprint et des rétrospectives, jusqu'à la livraison du travail terminé.

        **Nos outils au quotidien :** Excel, Power BI, Streamlit, GitHub, Discord, Google Drive, VS Code et Python.
        """)
    with col3:
        st.markdown("""
        **TetraData** est née de la rencontre de plusieurs experts en data, unis par la passion
        de transformer les données en décisions stratégiques pour des clients dans divers secteurs d'activité.

        Des entreprises comme **Coca-Cola, Netflix, Leboncoin, Air France** et **Peugeot** nous ont fait confiance.
        Nous sommes engagés autour de certifications reconnues : Lean 6 Sigma, label RSE et Great Place to Work.

        Notre équipe travaille selon la **méthode Agile** : à partir d'un Backlog Produit, nous planifions des sprints
        rythmés par des réunions d'équipe, des revues de sprint et des rétrospectives, jusqu'à la livraison du travail terminé.

        **Nos outils au quotidien :** Excel, Power BI, Streamlit, GitHub, Discord, Google Drive, VS Code et Python.
        """)