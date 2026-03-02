import streamlit as st
from streamlit_option_menu import option_menu
from PIL import Image
from src.ui import render_sidebar
from src.utils import load_css, pick_poster_url


def apply_opacity(image_path: str, opacity: float = 0.6) -> Image.Image:
    img = Image.open(image_path).convert("RGBA")
    r, g, b, a = img.split()
    a = a.point(lambda x: int(x * opacity))
    return Image.merge("RGBA", (r, g, b, a))

st.set_page_config(
    page_title="CinéData Creuse — TetraData",
    page_icon="🎬",
    layout="wide",
)

load_css()
render_sidebar()

# ─────────────────────────────────────────────
# HERO
# ─────────────────────────────────────────────
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

st.divider()

# ─────────────────────────────────────────────
# NAVIGATION — option_menu (remplace st.tabs)
# ─────────────────────────────────────────────
section = option_menu(
    menu_title=None,
    options=["Notre Projet", "La Creuse", "TetraData"],
    icons=["film", "geo-alt", "bar-chart-line"],
    orientation="horizontal",
    styles={
        "container": {"padding": "0", "background-color": "transparent"},
        "icon": {"color": "#e8a020", "font-size": "1rem"},
        "nav-link": {
            "font-size": "1rem",
            "letter-spacing": "0.08em",
            "color": "rgba(210,210,235,0.85)",
            "padding": "0.8rem 2rem",
            "--hover-color": "rgba(123,104,238,0.15)",
        },
        "nav-link-selected": {
            "background-color": "rgba(123,104,238,0.2)",
            "color": "#ffffff",
            "font-weight": "700",
            "border-bottom": "2px solid #7b68ee",
        },
    },
)

# ─────────────────────────────────────────────
# CONTENU PAR SECTION
# ─────────────────────────────────────────────

if section == "Notre Projet":

    st.markdown(
        "<div style='font-size:0.75rem;letter-spacing:0.18em;text-transform:uppercase;"
        "color:#616b6b;margin-bottom:0.2rem;'>TetraData</div>",
        unsafe_allow_html=True,
    )
    st.header("Le projet & l'organisation")

    # CSS flux (déplacé ici, injecté une seule fois au rendu de cette section)
    st.markdown(
        """
<style>
.flux-wrapper {
    position: relative;
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    padding: 2rem 1rem 1rem;
    margin-bottom: 0.5rem;
}
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
}
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
""",
        unsafe_allow_html=True,
    )

    st.markdown(
        """
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
  <div class="panel-label">CLIENT — Cinéma indépendant local</div>
  <div class="panel-desc">Acteur culturel essentiel de la Creuse, au cœur du territoire rural creusois.</div>
</div>
<div class="flux-panel" style="margin-bottom:0.6rem;">
  <div class="panel-label">CONSTAT — Baisse de fréquentation</div>
  <div class="panel-desc">Concurrence croissante des plateformes de streaming et désaffection du public.</div>
</div>
<div class="flux-panel" style="margin-bottom:0.6rem;">
  <div class="panel-label">BESOIN — Mieux comprendre</div>
  <div class="panel-desc">Comprendre les spectateurs et adapter l'offre pour regagner leur fidélité.</div>
</div>
<div class="flux-panel" style="margin-bottom:0.6rem;">
  <div class="panel-label">SOLUTION — Analyse de données</div>
  <div class="panel-desc">Moteur de recommandation personnalisée basé sur les données IMDb et TMDb.</div>
</div>
<div class="flux-panel" style="margin-bottom:0.6rem;">
  <div class="panel-label">LIVRABLES — Application + Dashboard</div>
  <div class="panel-desc">Appli spectateur + tableau de bord décisionnel pour l'équipe du cinéma.</div>
</div>
""",
        unsafe_allow_html=True,
    )


elif section == "La Creuse":
    # ── Contenu La Creuse à compléter ──
    st.header("La Creuse")
    st.image("assets/cartecreuse.jpg", use_container_width=True)


elif section == "TetraData":

    # ── CSS de l'onglet TetraData ──────────────────────────────────────────
    st.markdown("""
<style>
/* HERO BANNER */
.td-hero {
    position: relative;
    border-radius: 16px;
    overflow: hidden;
    margin-bottom: 2rem;
    min-height: 220px;
    background: linear-gradient(135deg, #0d0d1f 0%, #1a1040 50%, #0d1a2e 100%);
    display: flex;
    align-items: center;
    padding: 2.5rem 3rem;
    border: 1px solid rgba(123,104,238,0.3);
}
.td-hero::before {
    content: '';
    position: absolute;
    inset: 0;
    background:
        radial-gradient(circle at 80% 50%, rgba(123,104,238,0.18) 0%, transparent 60%),
        radial-gradient(circle at 20% 80%, rgba(232,160,32,0.12) 0%, transparent 50%);
}
.td-hero-logo { position: relative; z-index: 1; }
.td-hero-text { position: relative; z-index: 1; margin-left: 2.5rem; }
.td-hero-text h2 {
    font-family: 'Bebas Neue', Impact, sans-serif;
    font-size: 2.6rem;
    letter-spacing: 0.08em;
    color: #FFD700;
    margin: 0 0 0.4rem 0;
    filter: drop-shadow(0 0 10px rgba(255,200,0,0.4));
}
.td-hero-text p {
    font-size: 1.05rem;
    color: rgba(210,210,235,0.88);
    line-height: 1.65;
    max-width: 560px;
    margin: 0;
}

/* STAT CARDS */
.td-stats {
    display: flex;
    gap: 1rem;
    margin-bottom: 2rem;
}
.td-stat {
    flex: 1;
    background: rgba(123,104,238,0.08);
    border: 1px solid rgba(123,104,238,0.22);
    border-radius: 12px;
    padding: 1.4rem 1rem;
    text-align: center;
    transition: border-color 0.2s;
}
.td-stat:hover { border-color: rgba(123,104,238,0.55); }
.td-stat-number {
    font-family: 'Bebas Neue', Impact, sans-serif;
    font-size: 2.8rem;
    color: #FFD700;
    line-height: 1;
    filter: drop-shadow(0 0 8px rgba(255,200,0,0.35));
}
.td-stat-label {
    font-size: 0.78rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: rgba(190,190,220,0.75);
    margin-top: 6px;
}

/* SECTION CARDS */
.td-card {
    background: rgba(15,12,35,0.7);
    border: 1px solid rgba(123,104,238,0.18);
    border-radius: 14px;
    padding: 1.6rem 1.8rem;
    margin-bottom: 1.2rem;
    position: relative;
    overflow: hidden;
}
.td-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 4px; height: 100%;
    background: linear-gradient(180deg, #e8a020, #7b68ee);
    border-radius: 4px 0 0 4px;
}
.td-card-title {
    font-family: 'Bebas Neue', Impact, sans-serif;
    font-size: 1.35rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #e8a020;
    margin-bottom: 12px;
}
.td-card-img {
    width: 100%;
    border-radius: 8px;
    margin: 0.8rem 0;
    opacity: 0.85;
    object-fit: cover;
    max-height: 180px;
}
.td-card-body {
    font-size: 0.98rem;
    color: rgba(220,220,240,0.9);
    line-height: 1.75;
}

/* TEAM GRID */
.td-team {
    display: flex;
    gap: 1rem;
    margin-bottom: 2rem;
    flex-wrap: wrap;
}
.td-member {
    flex: 1;
    min-width: 140px;
    background: rgba(123,104,238,0.07);
    border: 1px solid rgba(123,104,238,0.2);
    border-radius: 12px;
    padding: 1.2rem 1rem;
    text-align: center;
}
.td-member-avatar {
    width: 56px; height: 56px;
    border-radius: 50%;
    background: linear-gradient(135deg, #7b68ee, #e8a020);
    display: flex; align-items: center; justify-content: center;
    font-size: 1.5rem;
    margin: 0 auto 10px;
}
.td-member-name {
    font-weight: 700;
    font-size: 0.9rem;
    color: #f0f0ff;
    margin-bottom: 3px;
}
.td-member-role {
    font-size: 0.75rem;
    color: #e8a020;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

/* BADGES */
.td-badges { display: flex; gap: 0.7rem; flex-wrap: wrap; margin-top: 0.8rem; }
.td-badge {
    background: rgba(232,160,32,0.12);
    border: 1px solid rgba(232,160,32,0.35);
    border-radius: 20px;
    padding: 0.3rem 0.9rem;
    font-size: 0.78rem;
    color: #e8a020;
    letter-spacing: 0.06em;
}

/* AGILE TIMELINE */
.td-timeline {
    display: flex;
    align-items: center;
    gap: 0;
    margin: 1rem 0;
    flex-wrap: wrap;
}
.td-tl-step {
    display: flex;
    flex-direction: column;
    align-items: center;
    flex: 1;
    min-width: 90px;
}
.td-tl-dot {
    width: 42px; height: 42px;
    border-radius: 50%;
    background: #1a1933;
    border: 2px solid #7b68ee;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem;
    margin-bottom: 8px;
    position: relative;
    z-index: 1;
}
.td-tl-label {
    font-size: 0.72rem;
    text-align: center;
    color: rgba(200,200,230,0.85);
    line-height: 1.3;
    max-width: 80px;
}
.td-tl-arrow {
    flex: 0 0 24px;
    text-align: center;
    color: #7b68ee;
    font-size: 1.1rem;
    margin-bottom: 28px;
}
</style>
""", unsafe_allow_html=True)

    # ── HERO ──────────────────────────────────────────────────────────────
    st.markdown("""
<div class="td-hero">
  <div class="td-hero-logo">
    <div style="font-family:'Bebas Neue',Impact,sans-serif;font-size:2.2rem;color:#FFD700;letter-spacing:0.1em;">TetraData</div>
  </div>
  <div class="td-hero-text">
    <h2>Transformons vos données en décisions</h2>
    <p>
      Née de la passion de plusieurs experts en data, TetraData accompagne les organisations
      dans leur transition vers une culture orientée données — du pipeline technique
      jusqu'à la prise de décision stratégique.
    </p>
  </div>
</div>
""", unsafe_allow_html=True)
    # Logo chargé via st.image pour éviter les problèmes de chemin
    col_logo, col_spacer = st.columns([1, 5])
    with col_logo:
        st.image("assets/logo_blanc_DT.png", width=160)

    # ── STATS ──────────────────────────────────────────────────────────────
    st.markdown("""
<div class="td-stats">
  <div class="td-stat">
    <div class="td-stat-number">5+</div>
    <div class="td-stat-label">Grands comptes</div>
  </div>
  <div class="td-stat">
    <div class="td-stat-number">3</div>
    <div class="td-stat-label">Certifications</div>
  </div>
  <div class="td-stat">
    <div class="td-stat-number">100%</div>
    <div class="td-stat-label">Méthode Agile</div>
  </div>
  <div class="td-stat">
    <div class="td-stat-number">∞</div>
    <div class="td-stat-label">Curiosité data</div>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── COLONNES PRINCIPALES ──────────────────────────────────────────────
    col_left, col_right = st.columns([1.1, 1], gap="large")

    with col_left:

        # ÉQUIPE
        st.markdown("""
<div class="td-card">
  <div class="td-card-title">L'équipe</div>
  <div class="td-team">
    <div class="td-member">
      <div class="td-member-avatar">📊</div>
      <div class="td-member-name">Anthony</div>
      <div class="td-member-role">Data Analyst</div>
    </div>
    <div class="td-member">
      <div class="td-member-avatar">🤖</div>
      <div class="td-member-name">Équipe ML</div>
      <div class="td-member-role">Data Scientist</div>
    </div>
    <div class="td-member">
      <div class="td-member-avatar">🎨</div>
      <div class="td-member-name">Équipe UX</div>
      <div class="td-member-role">Data Viz</div>
    </div>
    <div class="td-member">
      <div class="td-member-avatar">⚙️</div>
      <div class="td-member-name">Équipe Ops</div>
      <div class="td-member-role">Data Engineer</div>
    </div>
  </div>
  <div class="td-card-body" style="margin-top:0.5rem;">
    Une équipe pluridisciplinaire réunie autour d'une conviction commune :
    <strong style="color:#FFD700;">la donnée bien exploitée change tout.</strong>
  </div>
</div>
""", unsafe_allow_html=True)
        st.image("assets/img1.jpg", use_container_width=True)

        # MÉTHODE AGILE
        st.markdown("""
<div class="td-card">
  <div class="td-card-title">Notre méthode — Agile Scrum</div>
  <div class="td-timeline">
    <div class="td-tl-step">
      <div class="td-tl-dot">📋</div>
      <div class="td-tl-label">Backlog Produit</div>
    </div>
    <div class="td-tl-arrow">→</div>
    <div class="td-tl-step">
      <div class="td-tl-dot">🗓️</div>
      <div class="td-tl-label">Planification Sprint</div>
    </div>
    <div class="td-tl-arrow">→</div>
    <div class="td-tl-step">
      <div class="td-tl-dot">⚡</div>
      <div class="td-tl-label">Sprint 24h</div>
    </div>
    <div class="td-tl-arrow">→</div>
    <div class="td-tl-step">
      <div class="td-tl-dot">🔍</div>
      <div class="td-tl-label">Revue & Rétro</div>
    </div>
    <div class="td-tl-arrow">→</div>
    <div class="td-tl-step">
      <div class="td-tl-dot">✅</div>
      <div class="td-tl-label">Livraison</div>
    </div>
  </div>
  <div class="td-card-body">
    Chaque sprint est rythmé par des rituels courts et efficaces.
    On livre vite, on apprend encore plus vite.
  </div>
</div>
""", unsafe_allow_html=True)
        st.image("assets/img2.jpg", use_container_width=True)

    with col_right:

        # CLIENTS
        st.markdown("""
<div class="td-card">
  <div class="td-card-title">Ils nous font confiance</div>
  <div class="td-card-body">
    Des acteurs majeurs de leurs secteurs nous ont confié leurs défis data.
    De la grande consommation au transport en passant par le divertissement,
    TetraData s'adapte à chaque contexte.
  </div>
""", unsafe_allow_html=True)
        st.image("assets/logo_partenaires.png", use_container_width=True)
        st.image("assets/img3.jpg", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # CERTIFICATIONS
        st.markdown("""
<div class="td-card" style="margin-top:1.2rem;">
  <div class="td-card-title">Nos engagements & certifications</div>
  <div class="td-card-body">
    La qualité ne se décrète pas, elle se prouve. TetraData s'engage sur des standards
    reconnus dans l'industrie.
  </div>
  <div class="td-badges">
    <span class="td-badge">Lean 6 Sigma</span>
    <span class="td-badge">Label RSE</span>
    <span class="td-badge">Great Place to Work</span>
  </div>
</div>
""", unsafe_allow_html=True)

        # OUTILS
        st.markdown("""
<div class="td-card" style="margin-top:1.2rem;">
  <div class="td-card-title">Notre stack technique</div>
  <div class="td-badges">
    <span class="td-badge">Python</span>
    <span class="td-badge">Streamlit</span>
    <span class="td-badge">Power BI</span>
    <span class="td-badge">GitHub</span>
    <span class="td-badge">VS Code</span>
    <span class="td-badge">Excel</span>
    <span class="td-badge">Discord</span>
    <span class="td-badge">Google Drive</span>
  </div>
</div>
""", unsafe_allow_html=True)
