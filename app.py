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
st.image('assets/logo_noir.png')
# ---------------------------------------------------------------------
# HERO (base)
# ---------------------------------------------------------------------
left, right = st.columns([1.2, 1], gap="large")

with left:
    st.caption("🎥 Cinéma indépendant · Département 23")

    st.title("Le cinéma ancré dans la Creuse")
    st.write("**La data au service du cinéma de proximité.**")

    st.write(
        "CinéData Creuse naît de la rencontre entre un cinéma indépendant de la Creuse "
        "et la puissance de l'analyse de données. Moderniser sans perdre l'âme locale — "
        "c'est notre mission chez TetraData."
    )

    b1, b2 = st.columns(2)
    with b1:
        st.button("▶ Découvrir le projet", use_container_width=True)
    with b2:
        st.button("📍 Explorer la carte", use_container_width=True)

with right:
    st.subheader("Département de la Creuse — 23")
    st.caption("Aperçu (indicatif) des cinémas partenaires")

    # Optionnel : un mini SVG (tu peux supprimer ce bloc si tu veux 0 HTML)
    st.markdown(
        """
        <svg viewBox="0 0 400 360" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:auto;">
          <path d="
            M 80,40 C 90,30 110,25 130,28
            L 160,22 C 185,18 210,20 230,30
            L 260,28 C 290,25 320,35 340,50
            L 355,75 C 365,95 362,120 355,140
            L 360,165 C 368,190 365,215 355,235
            L 340,258 C 325,278 300,292 275,298
            L 250,310 C 225,318 200,320 175,315
            L 148,308 C 122,300 100,285 84,265
            L 65,242 C 48,220 42,195 45,170
            L 42,145 C 40,118 48,92 62,70
            Z" fill="currentColor" opacity="0.12" stroke="currentColor" stroke-width="2"/>

          <circle cx="195" cy="165" r="6" fill="currentColor" opacity="0.7"/>
          <text x="208" y="162" font-size="12" fill="currentColor">Guéret</text>

          <circle cx="248" cy="215" r="5" fill="currentColor" opacity="0.6"/>
          <text x="260" y="219" font-size="12" fill="currentColor">Aubusson</text>

          <circle cx="155" cy="225" r="5" fill="currentColor" opacity="0.55"/>
          <text x="105" y="222" font-size="11" fill="currentColor">Bourganeuf</text>

          <circle cx="112" cy="148" r="5" fill="currentColor" opacity="0.55"/>
          <text x="52" y="144" font-size="11" fill="currentColor">La Souterraine</text>
        </svg>
        """,
        unsafe_allow_html=True,
    )

st.divider()

# ---------------------------------------------------------------------
# SECTION : LE PROJET & L'ORGANISATION
# ---------------------------------------------------------------------
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

st.divider()

# ---------------------------------------------------------------------
# SECTION : CARTE / CINÉMAS LOCAUX (texte)
# ---------------------------------------------------------------------
st.header("Le cinéma en Creuse")
st.caption("Territoire")

a, b = st.columns([1, 1.2], gap="large")

with a:
    st.subheader("Vos cinémas locaux")
    st.write(
        "La Creuse compte plusieurs salles indépendantes qui font vivre la culture cinématographique "
        "dans ce territoire rural. CinéData Creuse connecte ces lieux à leurs publics grâce à la data."
    )

    st.write("**Cinémas partenaires (exemples)**")
    st.write("- Cinéma de la Creuse — Guéret · 2 salles · 300 places")
    st.write("- Le Ciné-Forum — Aubusson · 1 salle · 150 places")
    st.write("- Salle des Fêtes Cinéma — Bourganeuf · 1 salle · 120 places")
    st.write("- Cinéma La Souterraine — La Souterraine · 1 salle · 180 places")

with b:
    st.subheader("Carte (placeholder)")
    st.info(
        "Ici tu peux brancher une vraie carte plus tard (pydeck, folium, altair, "
        "ou une image). Pour l’instant c’est une base de layout."
    )

st.divider()

# ---------------------------------------------------------------------
# SECTION : ÉTUDE DE MARCHÉ
# ---------------------------------------------------------------------
st.header("Étude de marché")
st.caption("Sources : INSEE & CNC")

m1, m2 = st.columns(2, gap="large")

with m1:
    st.subheader("Démographie — Population")
    st.write("- Évolution de la population du département depuis les années 2000")
    st.write("- Population par tranches d'âge — majorité de +50 ans")
    st.write("- Benchmark habitants / département vs autres territoires")
    st.write("- Catégories socio-professionnelles (CSP) des habitants")

with m2:
    st.subheader("Cinéma — Fréquentation")
    st.write("- Répartition par âge de la fréquentation dans la région")
    st.write("- Entrées annuelles / habitant : Creuse vs autres départements")
    st.write("- Nombre d'écrans : Creuse vs autres départements")
    st.write("- Prix moyen d'une place vs plateformes de streaming")
    st.write("- Habitudes par genre et par âge / CSP")

st.caption("Sources : INSEE et CNC")

st.divider()

# ---------------------------------------------------------------------
# SECTION : ANALYSE DÉMOGRAPHIQUE (KPI)
# ---------------------------------------------------------------------
st.header("La Creuse — Analyse démographique")
st.caption("INSEE 2024")

k1, k2, k3, k4 = st.columns(4, gap="small")
with k1:
    st.metric("Habitants", "113 000", "↘ Population en baisse")
with k2:
    st.metric("Tranche d'âge majoritaire", "> 50 ans", "75,2% (indicatif)")
with k3:
    st.metric("Retraités (CSP)", "+50%", "Public prioritaire")
with k4:
    st.metric("Hommes / Femmes", "50 / 50", "48,19% H · 50,81% F")

d1, d2 = st.columns(2, gap="large")

with d1:
    st.subheader("Répartition par tranche d'âge (résumé)")
    st.write("- +50 ans : 75,2%")
    st.write("- 25–49 ans : 13,5%")
    st.write("- 15–24 ans : 6,8%")
    st.write("- 0–14 ans : 4,5%")

with d2:
    st.subheader("Catégories socio-professionnelles (résumé)")
    st.write("- Retraités : ~50%")
    st.write("- Ouvriers : ~18%")
    st.write("- Employés : ~12%")
    st.write("- Prof. intermédiaires : ~10%")
    st.write("- Autres : ~10%")

st.divider()

# ---------------------------------------------------------------------
# SECTION : CINÉMA EN CREUSE (insights)
# ---------------------------------------------------------------------
st.header("Le cinéma en Creuse")
st.caption("Analyse CNC")

# 2 lignes de 3 cartes (en Streamlit simple)
row1 = st.columns(3, gap="small")
row2 = st.columns(3, gap="small")

insights = [
    ("🎬", "Fréquentation par âge", "25–49 ans & +50",
     "Les 25–49 ans et les +50 ans sont les tranches les plus actives au cinéma."),
    ("📽️", "Nombre d'écrans", "12 écrans",
     "Parmi les départements les moins bien équipés (moyenne nationale : 65)."),
    ("📊", "Entrées / habitant", "1,58 / an",
     "En dessous de la moyenne nationale (2,43)."),
    ("🎭", "Genre n°1", "Comédie",
     "Comédies et animation dominent ; retraités : comédies & documentaires."),
    ("💳", "Prix moyen", "8€13",
     "Une place de cinéma reste compétitive face au streaming."),
    ("🏘️", "CSP & genres", "Neutre",
     "Le milieu social semble peu influencer les choix de films."),
]

for col, item in zip(row1 + row2, insights):
    ico, title, value, desc = item
    with col:
        st.write(f"### {ico} {title}")
        st.write(f"**{value}**")
        st.caption(desc)

st.subheader("Parts de marché par genre — Cinémas de la Creuse (résumé)")
st.write("- Comédie : 40,3%")
st.write("- Animation : 36,3%")
st.write("- Drame : 14,4%")
st.write("- Action : 7,9%")
st.caption("Source : CNC — Données 2024")

st.divider()

# ---------------------------------------------------------------------
# CITATION
# ---------------------------------------------------------------------
st.subheader("Parole du terrain")
st.write(
    "« Nous voulons nous moderniser sans perdre notre identité locale. "
    "Nous avons besoin d'un outil simple pour mieux connaître notre public. »"
)
st.caption("— Direction du Cinéma Indépendant de la Creuse")

st.divider()

# ---------------------------------------------------------------------
# FOOTER (simple)
# ---------------------------------------------------------------------
f1, f2, f3 = st.columns([2, 1, 1], gap="large")

with f1:
    st.write("**CinéData Creuse** — par **TetraData**")
    st.caption(
        "Cabinet spécialisé en analyse de données et tableaux de bord décisionnels "
        "pour les acteurs culturels et territoriaux."
    )

with f2:
    st.write("**Navigation (base)**")
    st.write("- Le Projet")
    st.write("- Étude de marché")
    st.write("- Démographie")
    st.write("- Cinéma en Creuse")
    st.write("- Carte")

with f3:
    st.write("**TetraData**")
    st.write("- Notre mission")
    st.write("- À propos")
    st.write("- Contact")
    st.write("- Mentions légales")

st.caption("© 2025 CinéData Creuse — Conçu par TetraData")