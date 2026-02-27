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

<div style="text-align:center; margin: 2rem 0 2rem 0; padding: 0 1rem;">
  <div style="
      font-size: 0.72rem;
      letter-spacing: 0.28em;
      text-transform: uppercase;
      color: #e8a020;
      margin-bottom: 14px;
  ">
    <span style="display:inline-block;width:28px;height:1px;background:#e8a020;vertical-align:middle;margin-right:10px;"></span>
    Cinéma Indépendant · Département 23
    <span style="display:inline-block;width:28px;height:1px;background:#e8a020;vertical-align:middle;margin-left:10px;"></span>
  </div>
  <div style="
      font-family:'Bebas Neue', Impact, sans-serif;
      font-size: clamp(2.2rem, 5vw, 4.2rem);
      letter-spacing: 0.04em;
      color: #ffffff;
      line-height: 1.05;
      margin-bottom: 18px;
  ">
    Le cinéma ancré dans la Creuse
  </div>
  <div style="
      font-size: 1.15rem;
      font-weight: 700;
      color: #f0f0f0;
      margin-bottom: 14px;
      letter-spacing: 0.02em;
  ">
    La data au service du cinéma de proximité.
  </div>
  <div style="
      font-size: 0.97rem;
      font-style: italic;
      color: rgba(180,180,200,0.9);
      line-height: 1.85;
      max-width: 540px;
      margin: 0 auto;
  ">
    CinéData Creuse naît de la rencontre entre un cinéma indépendant de la Creuse
    et la puissance de l'analyse de données. Moderniser sans perdre l'âme locale —
    c'est notre mission chez TetraData.
  </div>
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

with tab1:

    st.markdown("<div style='font-size:0.75rem;letter-spacing:0.18em;text-transform:uppercase;color:#616b6b;margin-bottom:0.2rem;'>TetraData</div>", unsafe_allow_html=True)
    st.header("Le projet & l'organisation")

    # ── Flux visuel ──────────────────────────────────────────────────────────
    st.markdown("""
<style>
.flux-wrapper {
    position: relative;
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    padding: 2rem 1rem 1rem;
    margin-bottom: 0.5rem;
}
/* Ligne horizontale de connexion */
.flux-wrapper::before {
    content: '';
    position: absolute;
    top: 68px;
    left: 10%;
    right: 10%;
    height: 2px;
    background: linear-gradient(90deg, #e8a020, #7b68ee, #e8a020, #7b68ee, #e8a020);
    opacity: 0.4;
    z-index: 0;
}
.flux-step {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    flex: 1;
    position: relative;
    z-index: 1;
}
.flux-circle {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    background: #1a1933;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.9rem;
    margin-bottom: 14px;
    transition: transform 0.2s ease;
}
.flux-circle:hover { transform: scale(1.08); }
.flux-label {
    font-family: 'Bebas Neue', Impact, sans-serif;
    font-size: 1.05rem;
    letter-spacing: 0.14em;
    margin-bottom: 6px;
}
.flux-title {
    font-size: 0.82rem;
    color: rgba(230,238,238,0.85);
    line-height: 1.4;
    max-width: 120px;
}
/* Panneau description */
.flux-panel {
    background: rgba(123,104,238,0.08);
    border: 1px solid rgba(123,104,238,0.25);
    border-radius: 12px;
    padding: 1rem 1.5rem;
    margin-top: 0.5rem;
    text-align: center;
}
.flux-panel .panel-label {
    font-size: 0.78rem;
    color: #e8a020;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 6px;
}
.flux-panel .panel-desc {
    font-size: 1rem;
    color: rgba(232,245,233,0.92);
    line-height: 1.6;
}
</style>
""", unsafe_allow_html=True)

    st.markdown(f"""
<div class="flux-wrapper">
  <div class="flux-step">
    <div class="flux-circle" style="border:2px solid #e8a020;box-shadow:0 0 18px #e8a02033;">
      <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#e8a020" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
        <rect x="2" y="3" width="20" height="14" rx="2"/><path d="M8 21h8M12 17v4"/>
        <path d="M10 10l5-3v6l-5-3z"/>
      </svg>
    </div>
    <div class="flux-label" style="color:#e8a020;">CLIENT</div>
    <div class="flux-title">Cinéma indépendant local</div>
  </div>
  <div class="flux-step">
    <div class="flux-circle" style="border:2px solid #7b68ee;box-shadow:0 0 18px #7b68ee33;">
      <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#7b68ee" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
        <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
      </svg>
    </div>
    <div class="flux-label" style="color:#7b68ee;">CONSTAT</div>
    <div class="flux-title">Baisse de fréquentation</div>
  </div>
  <div class="flux-step">
    <div class="flux-circle" style="border:2px solid #e8a020;box-shadow:0 0 18px #e8a02033;">
      <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#e8a020" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>
      </svg>
    </div>
    <div class="flux-label" style="color:#e8a020;">BESOIN</div>
    <div class="flux-title">Mieux comprendre</div>
  </div>
  <div class="flux-step">
    <div class="flux-circle" style="border:2px solid #7b68ee;box-shadow:0 0 18px #7b68ee33;">
      <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#7b68ee" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
        <path d="M12 2a7 7 0 0 1 7 7c0 4-3 6-3 9H8c0-3-3-5-3-9a7 7 0 0 1 7-7z"/><path d="M9 17h6"/><path d="M9 21h6"/>
      </svg>
    </div>
    <div class="flux-label" style="color:#7b68ee;">SOLUTION</div>
    <div class="flux-title">Analyse de données</div>
  </div>
  <div class="flux-step">
    <div class="flux-circle" style="border:2px solid #e8a020;box-shadow:0 0 18px #e8a02033;">
      <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#e8a020" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
        <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
        <polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/>
      </svg>
    </div>
    <div class="flux-label" style="color:#e8a020;">LIVRABLES</div>
    <div class="flux-title">Application + Dashboard</div>
  </div>
</div>

<div class="flux-panel" style="margin-bottom:0.6rem;">
  <div class="panel-label">🎬 CLIENT — Cinéma indépendant local</div>
  <div class="panel-desc">Acteur culturel essentiel de la Creuse, au cœur du territoire rural creusois.</div>
</div>
<div class="flux-panel" style="margin-bottom:0.6rem;">
  <div class="panel-label">📉 CONSTAT — Baisse de fréquentation</div>
  <div class="panel-desc">Concurrence croissante des plateformes de streaming et désaffection du public.</div>
</div>
<div class="flux-panel" style="margin-bottom:0.6rem;">
  <div class="panel-label">🎯 BESOIN — Mieux comprendre</div>
  <div class="panel-desc">Comprendre les spectateurs et adapter l'offre pour regagner leur fidélité.</div>
</div>
<div class="flux-panel" style="margin-bottom:0.6rem;">
  <div class="panel-label">💡 SOLUTION — Analyse de données</div>
  <div class="panel-desc">Moteur de recommandation personnalisée basé sur les données IMDb et TMDb.</div>
</div>
<div class="flux-panel" style="margin-bottom:0.6rem;">
  <div class="panel-label">📦 LIVRABLES — Application + Dashboard</div>
  <div class="panel-desc">Appli spectateur + tableau de bord décisionnel pour l'équipe du cinéma.</div>
</div>
""", unsafe_allow_html=True)

    st.image("assets/logo_bandeau_orga.png", use_container_width=True)



with tab3:
    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.markdown("<div style='margin-top: 4rem;'>", unsafe_allow_html=True)
        st.image("assets/logo_blanc_DT.png", width=300)
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style="font-size: 1.25rem; line-height: 1.8;">

        <strong>TetraData</strong> est née de la rencontre de plusieurs experts en data, unis par la passion
        de transformer les données en décisions stratégiques pour des clients dans divers secteurs d'activité.

        <br><br>Des entreprises comme <strong>Coca-Cola, Netflix, Leboncoin, Air France</strong> et <strong>Peugeot</strong> nous ont fait confiance.
        Nous sommes engagés autour de certifications reconnues : Lean 6 Sigma, label RSE et Great Place to Work.

        <br><br>Notre équipe travaille selon la <strong>méthode Agile</strong> : à partir d'un Backlog Produit, nous planifions des sprints
        rythmés par des réunions d'équipe, des revues de sprint et des rétrospectives, jusqu'à la livraison du travail terminé.

        <br><br><strong>Nos outils au quotidien :</strong> Excel, Power BI, Streamlit, GitHub, Discord, Google Drive, VS Code et Python.

        </div>
        """, unsafe_allow_html=True)

    col_left, col_mid, col_right = st.columns([0.1, 2, 1.5])
    with col_left:
        pass
    with col_mid:
        st.image("assets/logo_partenaires.png", use_container_width=True)

