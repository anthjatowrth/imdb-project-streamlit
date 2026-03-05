import streamlit as st
from streamlit_option_menu import option_menu
from PIL import Image
import base64
from pathlib import Path
from src.ui import render_sidebar
from src.utils import load_css, pick_poster_url


def apply_opacity(image_path: str, opacity: float = 0.6) -> Image.Image:
    img = Image.open(image_path).convert("RGBA")
    r, g, b, a = img.split()
    a = a.point(lambda x: int(x * opacity))
    return Image.merge("RGBA", (r, g, b, a))


def img_to_b64(path: str) -> str:
    """Convertit une image locale en base64 pour injection HTML."""
    try:
        data = Path(path).read_bytes()
        ext = Path(path).suffix.lower().replace(".", "")
        mime = "jpeg" if ext == "jpg" else ext
        return f"data:image/{mime};base64,{base64.b64encode(data).decode()}"
    except Exception:
        return ""


st.set_page_config(page_title="CineData Creuse - TetraData", page_icon="cinema", layout="wide")
load_css()
render_sidebar()

# ================================================================
# PAGE HERO
# ================================================================
st.markdown("""
<div style="text-align:center;margin:0.2rem 0 1.5rem 0;">
  <div style="font-family:'Bebas Neue',Impact,sans-serif;font-size:clamp(3rem,5vw,5rem);
      letter-spacing:0.08em;text-transform:uppercase;color:#FFD700;
      filter:drop-shadow(0 0 12px rgba(255,200,0,0.5));">
    Bienvenue sur CineData
  </div>
  <div style="color:rgba(210,210,235,0.9);font-size:1.15rem;margin-top:0.3rem;letter-spacing:0.04em;">
    Explore, decouvre et trouve ton prochain chef-d'oeuvre.
  </div>
  <div style="width:120px;height:3px;margin:20px auto 0;
      background:linear-gradient(90deg,transparent,#7b68ee,transparent);
      box-shadow:0 0 15px rgba(123,104,238,0.6);"></div>
</div>
<div style="text-align:center;margin:2rem 0;padding:0 1rem;">
  <div style="font-size:0.72rem;letter-spacing:0.28em;text-transform:uppercase;color:#e8a020;margin-bottom:14px;">
    <span style="display:inline-block;width:28px;height:1px;background:#e8a020;vertical-align:middle;margin-right:10px;"></span>
    Cinema Independant - Departement 23
    <span style="display:inline-block;width:28px;height:1px;background:#e8a020;vertical-align:middle;margin-left:10px;"></span>
  </div>
  <div style="font-family:'Bebas Neue',Impact,sans-serif;font-size:clamp(2.2rem,5vw,4.2rem);
      letter-spacing:0.04em;color:#ffffff;line-height:1.05;margin-bottom:18px;">
    Le cinema ancre dans la Creuse
  </div>
  <div style="font-size:1.15rem;font-weight:700;color:#f0f0f0;margin-bottom:14px;letter-spacing:0.02em;">
    La data au service du cinema de proximite.
  </div>
  <div style="font-size:0.97rem;font-style:italic;color:rgba(180,180,200,0.9);line-height:1.85;max-width:540px;margin:0 auto;">
    CineData Creuse nait de la rencontre entre un cinema independant de la Creuse
    et la puissance de l'analyse de donnees. Moderniser sans perdre l'ame locale,
    c'est notre mission chez TetraData.
  </div>
</div>
""", unsafe_allow_html=True)

st.divider()

# ================================================================
# NAVIGATION
# ================================================================
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

# ================================================================
# NOTRE PROJET
# ================================================================
if section == "Notre Projet":
    st.markdown(
        "<div style='font-size:0.75rem;letter-spacing:0.18em;text-transform:uppercase;"
        "color:#616b6b;margin-bottom:0.2rem;'>TetraData</div>",
        unsafe_allow_html=True,
    )
    st.header("Le projet & l'organisation")

    st.markdown("""
<style>
.flux-wrapper {
    position:relative;display:flex;align-items:flex-start;
    justify-content:space-between;padding:2rem 1rem 1rem;margin-bottom:0.5rem;
}
.flux-wrapper::before {
    content:'';position:absolute;top:68px;left:10%;right:10%;height:2px;
    background:linear-gradient(90deg,#e8a020,#7b68ee,#e8a020,#7b68ee,#e8a020);
    opacity:0.4;z-index:0;
}
.flux-step {display:flex;flex-direction:column;align-items:center;text-align:center;flex:1;position:relative;z-index:1;}
.flux-circle {width:80px;height:80px;border-radius:50%;background:#1a1933;display:flex;align-items:center;justify-content:center;font-size:1.9rem;margin-bottom:14px;}
.flux-label {font-family:'Bebas Neue',Impact,sans-serif;font-size:1.05rem;letter-spacing:0.14em;margin-bottom:6px;}
.flux-title {font-size:0.82rem;color:rgba(230,238,238,0.85);line-height:1.4;max-width:120px;}
.flux-panel {background:rgba(123,104,238,0.08);border:1px solid rgba(123,104,238,0.25);border-radius:12px;padding:1rem 1.5rem;margin-top:0.5rem;text-align:center;}
.flux-panel .panel-label {font-size:0.78rem;color:#e8a020;letter-spacing:0.12em;text-transform:uppercase;margin-bottom:6px;}
.flux-panel .panel-desc {font-size:1rem;color:rgba(232,245,233,0.92);line-height:1.6;}
</style>
""", unsafe_allow_html=True)

    st.markdown("""
<div class="flux-wrapper">
  <div class="flux-step">
    <div class="flux-circle" style="border:2px solid #e8a020;box-shadow:0 0 18px #e8a02033;">
      <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#e8a020" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
        <rect x="2" y="3" width="20" height="14" rx="2"/><path d="M8 21h8M12 17v4"/><path d="M10 10l5-3v6l-5-3z"/>
      </svg>
    </div>
    <div class="flux-label" style="color:#e8a020;">CLIENT</div>
    <div class="flux-title">Cinema independant local</div>
  </div>
  <div class="flux-step">
    <div class="flux-circle" style="border:2px solid #7b68ee;box-shadow:0 0 18px #7b68ee33;">
      <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#7b68ee" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
        <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
      </svg>
    </div>
    <div class="flux-label" style="color:#7b68ee;">CONSTAT</div>
    <div class="flux-title">Baisse de frequentation</div>
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
    <div class="flux-title">Analyse de donnees</div>
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
<div class="flux-panel" style="margin-bottom:0.6rem;"><div class="panel-label">CLIENT - Cinema independant local</div><div class="panel-desc">Acteur culturel essentiel de la Creuse, au coeur du territoire rural creusois.</div></div>
<div class="flux-panel" style="margin-bottom:0.6rem;"><div class="panel-label">CONSTAT - Baisse de frequentation</div><div class="panel-desc">Concurrence croissante des plateformes de streaming et desaffection du public.</div></div>
<div class="flux-panel" style="margin-bottom:0.6rem;"><div class="panel-label">BESOIN - Mieux comprendre</div><div class="panel-desc">Comprendre les spectateurs et adapter l'offre pour regagner leur fidelite.</div></div>
<div class="flux-panel" style="margin-bottom:0.6rem;"><div class="panel-label">SOLUTION - Analyse de donnees</div><div class="panel-desc">Moteur de recommandation personnalisee base sur les donnees IMDb et TMDb.</div></div>
<div class="flux-panel" style="margin-bottom:0.6rem;"><div class="panel-label">LIVRABLES - Application + Dashboard</div><div class="panel-desc">Appli spectateur + tableau de bord decisionnel pour l'equipe du cinema.</div></div>
""", unsafe_allow_html=True)

# ================================================================
# LA CREUSE
# ================================================================
elif section == "La Creuse":
    st.header("La Creuse")
    st.image("assets/cartecreuse.jpg", use_container_width=True)


# ================================================================
# TETRADATA
# ================================================================
elif section == "TetraData":

    st.markdown("""
<style>
.td-hero {
    position:relative;border-radius:16px;overflow:hidden;
    background:linear-gradient(135deg,#0d0d1f 0%,#1a1040 50%,#0d1a2e 100%);
    display:flex;align-items:center;padding:2.5rem 3rem;
    border:1px solid rgba(123,104,238,0.3);min-height:180px;
}
.td-hero::before {
    content:'';position:absolute;inset:0;
    background:radial-gradient(circle at 80% 50%,rgba(123,104,238,0.18) 0%,transparent 60%),
               radial-gradient(circle at 20% 80%,rgba(232,160,32,0.12) 0%,transparent 50%);
}
.td-hero-text {position:relative;z-index:1;}
.td-hero-text h2 {font-family:'Bebas Neue',Impact,sans-serif;font-size:2.4rem;letter-spacing:0.08em;color:#FFD700;margin:0 0 0.4rem 0;filter:drop-shadow(0 0 10px rgba(255,200,0,0.4));}
.td-hero-text p {font-size:1.05rem;color:rgba(210,210,235,0.88);line-height:1.65;max-width:560px;margin:0;}
.td-stats {display:flex;gap:1rem;margin-bottom:2rem;}
.td-stat {flex:1;background:rgba(123,104,238,0.08);border:1px solid rgba(123,104,238,0.22);border-radius:12px;padding:1.4rem 1rem;text-align:center;}
.td-stat-number {font-family:'Bebas Neue',Impact,sans-serif;font-size:2.8rem;color:#FFD700;line-height:1;filter:drop-shadow(0 0 8px rgba(255,200,0,0.35));}
.td-stat-label {font-size:0.78rem;letter-spacing:0.14em;text-transform:uppercase;color:rgba(190,190,220,0.75);margin-top:6px;}
.td-card {background:rgba(15,12,35,0.7);border:1px solid rgba(123,104,238,0.18);border-radius:14px;padding:1.6rem 1.8rem;margin-bottom:1.2rem;position:relative;overflow:hidden;}
.td-card::before {content:'';position:absolute;top:0;left:0;width:4px;height:100%;background:linear-gradient(180deg,#e8a020,#7b68ee);border-radius:4px 0 0 4px;}
.td-card-title {font-family:'Bebas Neue',Impact,sans-serif;font-size:1.35rem;letter-spacing:0.14em;text-transform:uppercase;color:#e8a020;margin-bottom:12px;}
.td-card-body {font-size:0.98rem;color:rgba(220,220,240,0.9);line-height:1.75;}
.td-team {display:flex;gap:1rem;margin-bottom:1rem;flex-wrap:wrap;}
.td-member {flex:1;min-width:140px;background:rgba(123,104,238,0.07);border:1px solid rgba(123,104,238,0.2);border-radius:12px;padding:1.2rem 1rem;text-align:center;}
.td-member-avatar {width:56px;height:56px;border-radius:50%;background:linear-gradient(135deg,#7b68ee,#e8a020);display:flex;align-items:center;justify-content:center;font-size:1.5rem;margin:0 auto 10px;}
.td-member-name {font-weight:700;font-size:0.9rem;color:#f0f0ff;margin-bottom:3px;}
.td-member-role {font-size:0.75rem;color:#e8a020;letter-spacing:0.08em;text-transform:uppercase;}
.td-cert-grid {display:flex;gap:1rem;margin-top:1rem;}
.td-cert-tile {flex:1;background:rgba(123,104,238,0.07);border:1px solid rgba(123,104,238,0.2);border-radius:12px;padding:1.2rem 0.8rem;text-align:center;}
.td-cert-img {width:90px;height:90px;border-radius:10px;background:#fff;display:flex;align-items:center;justify-content:center;margin:0 auto 10px;overflow:hidden;padding:6px;box-shadow:0 2px 10px rgba(0,0,0,0.3);}
.td-cert-img img {max-width:100%;max-height:100%;object-fit:contain;display:block;}
.td-cert-name {font-weight:700;font-size:0.85rem;color:#f0f0ff;margin-bottom:3px;line-height:1.3;}
.td-cert-type {font-size:0.72rem;color:#e8a020;letter-spacing:0.08em;text-transform:uppercase;}
.td-tools {display:flex;flex-wrap:wrap;gap:1.4rem;align-items:center;margin-top:1rem;}
.td-tool {text-align:center;min-width:58px;}
.td-tool img {height:36px;display:block;margin:0 auto;}
.td-tool-label {font-size:0.68rem;color:rgba(200,200,230,0.75);margin-top:5px;}
.agile-card {background:rgba(15,12,35,0.85);border:1px solid rgba(123,104,238,0.25);border-radius:16px;padding:1.8rem;margin-bottom:1.2rem;position:relative;overflow:hidden;}
.agile-card::before {content:'';position:absolute;top:0;left:0;width:4px;height:100%;background:linear-gradient(180deg,#e8a020,#7b68ee);border-radius:4px 0 0 4px;}
.agile-card::after {content:'';position:absolute;top:-60px;right:-60px;width:180px;height:180px;border-radius:50%;background:radial-gradient(circle,rgba(123,104,238,0.12) 0%,transparent 70%);pointer-events:none;}
.agile-title {font-family:'Bebas Neue',Impact,sans-serif;font-size:1.35rem;letter-spacing:0.14em;text-transform:uppercase;color:#e8a020;margin-bottom:6px;}
.agile-subtitle {font-size:0.82rem;color:rgba(180,180,210,0.7);letter-spacing:0.1em;text-transform:uppercase;margin-bottom:1.4rem;padding-bottom:0.8rem;border-bottom:1px solid rgba(123,104,238,0.15);}
.agile-steps {display:flex;flex-direction:column;position:relative;}
.agile-steps::before {content:'';position:absolute;left:21px;top:22px;bottom:22px;width:2px;background:linear-gradient(180deg,#e8a020,#7b68ee,#e8a020,#7b68ee);opacity:0.35;}
.agile-step {display:flex;align-items:flex-start;gap:1rem;padding:0.65rem 0;position:relative;}
.agile-step-dot {width:44px;height:44px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-family:'Bebas Neue',Impact,sans-serif;font-size:1.2rem;font-weight:bold;flex-shrink:0;position:relative;z-index:1;}
.agile-step-content {flex:1;padding-top:6px;}
.agile-step-name {font-weight:700;font-size:0.95rem;color:#f0f0ff;margin-bottom:3px;}
.agile-step-desc {font-size:0.78rem;color:rgba(180,180,210,0.7);line-height:1.4;}
.agile-step-tag {display:inline-block;background:rgba(232,160,32,0.12);border:1px solid rgba(232,160,32,0.3);border-radius:10px;padding:1px 8px;font-size:0.67rem;color:#e8a020;letter-spacing:0.06em;margin-top:4px;}
.agile-footer {margin-top:1.4rem;padding-top:1rem;border-top:1px solid rgba(123,104,238,0.15);display:flex;align-items:center;gap:0.8rem;}
.agile-footer-icon {width:36px;height:36px;border-radius:50%;background:rgba(123,104,238,0.15);border:1px solid rgba(123,104,238,0.3);display:flex;align-items:center;justify-content:center;font-size:1rem;flex-shrink:0;}
.agile-footer-text {font-size:0.88rem;color:rgba(220,220,240,0.85);font-style:italic;line-height:1.5;}
</style>
""", unsafe_allow_html=True)

    # ── HERO + LOGO ───────────────────────────────────────────────────────
    col_hero_text, col_hero_logo = st.columns([2.2, 1], gap="large")
    with col_hero_text:
        st.markdown("""
<div class="td-hero">
  <div class="td-hero-text">
    <h2>Transformons vos donnees en decisions</h2>
    <p>
      Nee de la passion de plusieurs experts en data, TetraData accompagne les organisations
      dans leur transition vers une culture orientee donnees, du pipeline technique
      jusqu'a la prise de decision strategique.
    </p>
  </div>
</div>
""", unsafe_allow_html=True)
    with col_hero_logo:
        st.markdown("<div style='height:1.5rem;'></div>", unsafe_allow_html=True)
        st.image("assets/logo_blanc_DT.png", use_container_width=True)

    # ── STATS ─────────────────────────────────────────────────────────────
    st.markdown("""
<div class="td-stats">
  <div class="td-stat"><div class="td-stat-number">5+</div><div class="td-stat-label">Grands comptes</div></div>
  <div class="td-stat"><div class="td-stat-number">3</div><div class="td-stat-label">Certifications</div></div>
  <div class="td-stat"><div class="td-stat-number">100%</div><div class="td-stat-label">Methode Agile</div></div>
  <div class="td-stat"><div class="td-stat-number">inf</div><div class="td-stat-label">Curiosite data</div></div>
</div>
""", unsafe_allow_html=True)

    col_left, col_right = st.columns([1.1, 1], gap="large")

    # ── COLONNE GAUCHE ────────────────────────────────────────────────────
    with col_left:

        st.markdown("""
<div class="td-card">
  <div class="td-card-title">L'equipe</div>
  <div class="td-team">
    <div class="td-member">
      <div class="td-member-avatar">&#128202;</div>
      <div class="td-member-name">Scrum Master</div>
      <div class="td-member-role">Data Analyst</div>
    </div>
    <div class="td-member">
      <div class="td-member-avatar">&#129302;</div>
      <div class="td-member-name">Equipe ML</div>
      <div class="td-member-role">Data Scientist</div>
    </div>
    <div class="td-member">
      <div class="td-member-avatar">&#127912;</div>
      <div class="td-member-name">Equipe UX</div>
      <div class="td-member-role">Data Viz</div>
    </div>
    <div class="td-member">
      <div class="td-member-avatar">&#9881;</div>
      <div class="td-member-name">Equipe Ops</div>
      <div class="td-member-role">Data Engineer</div>
    </div>
  </div>
  <div class="td-card-body" style="margin-top:0.5rem;">
    Une equipe pluridisciplinaire reunie autour d'une conviction commune :
    <strong style="color:#FFD700;">la donnee bien exploitee change tout.</strong>
  </div>
</div>
""", unsafe_allow_html=True)
        st.image("assets/img1.jpg", use_container_width=True)

        # AGILE — utilise une f-string Python classique, pas de triple-quote imbriquee
        agile_html = (
            '<div class="agile-card">'
            '<div class="agile-title">Notre methode - Agile Scrum</div>'
            '<div class="agile-subtitle">Framework iteratif &bull; Sprints de 24h</div>'
            '<div class="agile-steps">'

            '<div class="agile-step">'
            '<div class="agile-step-dot" style="background:rgba(232,160,32,0.15);border:2px solid #e8a020;color:#e8a020;">1</div>'
            '<div class="agile-step-content">'
            '<div class="agile-step-name">Backlog Produit</div>'
            '<div class="agile-step-desc">Recensement et priorisation de toutes les fonctionnalites a livrer.</div>'
            '<span class="agile-step-tag">Product Owner</span>'
            '</div></div>'

            '<div class="agile-step">'
            '<div class="agile-step-dot" style="background:rgba(123,104,238,0.15);border:2px solid #7b68ee;color:#7b68ee;">2</div>'
            '<div class="agile-step-content">'
            '<div class="agile-step-name">Planification du Sprint</div>'
            '<div class="agile-step-desc">Selection des taches, estimation de la charge, organisation de l\'equipe.</div>'
            '<span class="agile-step-tag">Equipe complete</span>'
            '</div></div>'

            '<div class="agile-step">'
            '<div class="agile-step-dot" style="background:rgba(232,160,32,0.15);border:2px solid #e8a020;color:#e8a020;">3</div>'
            '<div class="agile-step-content">'
            '<div class="agile-step-name">Sprint actif</div>'
            '<div class="agile-step-desc">Developpement intensif, daily stand-up de 15 min, iterations rapides.</div>'
            '<span class="agile-step-tag">24h / cycle</span>'
            '</div></div>'

            '<div class="agile-step">'
            '<div class="agile-step-dot" style="background:rgba(123,104,238,0.15);border:2px solid #7b68ee;color:#7b68ee;">4</div>'
            '<div class="agile-step-content">'
            '<div class="agile-step-name">Revue et Retrospective</div>'
            '<div class="agile-step-desc">Demo du travail termine, analyse des points d\'amelioration.</div>'
            '<span class="agile-step-tag">Feedback continu</span>'
            '</div></div>'

            '<div class="agile-step">'
            '<div class="agile-step-dot" style="background:linear-gradient(135deg,#e8a020,#7b68ee);border:2px solid #FFD700;color:#fff;">5</div>'
            '<div class="agile-step-content">'
            '<div class="agile-step-name">Livraison</div>'
            '<div class="agile-step-desc">Deploiement du livrable valide, documentation et passation client.</div>'
            '<span class="agile-step-tag" style="background:rgba(255,215,0,0.12);border-color:rgba(255,215,0,0.4);color:#FFD700;">Deliverable</span>'
            '</div></div>'

            '</div>'  # end agile-steps

            '<div class="agile-footer">'
            '<div class="agile-footer-icon">&#9654;</div>'
            '<div class="agile-footer-text">'
            'On livre vite, on apprend encore plus vite. '
            '<strong style="color:#FFD700;">Chaque sprint est une nouvelle opportunite de progresser.</strong>'
            '</div></div>'

            '</div>'  # end agile-card
        )
        st.markdown(agile_html, unsafe_allow_html=True)

    # ── COLONNE DROITE ────────────────────────────────────────────────────
    with col_right:

        st.markdown("""
<div class="td-card">
  <div class="td-card-title">Ils nous font confiance</div>
  <div class="td-card-body">
    Des acteurs majeurs de leurs secteurs nous ont confie leurs defis data.
    De la grande consommation au transport en passant par le divertissement,
    TetraData s'adapte a chaque contexte.
  </div>
</div>
""", unsafe_allow_html=True)
        st.image("assets/logo_partenaires.png", use_container_width=True)
        st.image("assets/img3.jpg", use_container_width=True)

        # ── CERTIFICATIONS — images encodees en base64 pour s'afficher dans le HTML
        lss_src  = img_to_b64("assets/LSS.png")
        rse_src  = img_to_b64("assets/RSE.png")
        gptw_src = img_to_b64("assets/GPTW.png")

        cert_html = (
            '<div class="td-card" style="margin-top:1.2rem;">'
            '<div class="td-card-title">Nos engagements et certifications</div>'
            '<div class="td-card-body" style="margin-bottom:1rem;">'
            "La qualite ne se decrete pas, elle se prouve. TetraData s'engage "
            "sur des standards reconnus dans l'industrie."
            '</div>'
            '<div class="td-cert-grid">'

            '<div class="td-cert-tile">'
            '<div class="td-cert-img">'
            f'<img src="{lss_src}" alt="Lean 6 Sigma"/>'
            '</div>'
            '<div class="td-cert-name">Lean 6 Sigma</div>'
            '<div class="td-cert-type">Certification</div>'
            '</div>'

            '<div class="td-cert-tile">'
            '<div class="td-cert-img">'
            f'<img src="{rse_src}" alt="Label RSE"/>'
            '</div>'
            '<div class="td-cert-name">Label RSE</div>'
            '<div class="td-cert-type">Engagement</div>'
            '</div>'

            '<div class="td-cert-tile">'
            '<div class="td-cert-img">'
            f'<img src="{gptw_src}" alt="Great Place to Work"/>'
            '</div>'
            '<div class="td-cert-name">Great Place to Work</div>'
            '<div class="td-cert-type">Label</div>'
            '</div>'

            '</div>'  # td-cert-grid
            '</div>'  # td-card
        )
        st.markdown(cert_html, unsafe_allow_html=True)

        # ── STACK TECHNIQUE ───────────────────────────────────────────────
        st.markdown("""
<div class="td-card" style="margin-top:1.2rem;">
  <div class="td-card-title">Notre stack technique</div>
  <div class="td-tools">
    <div class="td-tool">
      <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg" onerror="this.style.display='none'"/>
      <div class="td-tool-label">Python</div>
    </div>
    <div class="td-tool">
      <img src="https://streamlit.io/images/brand/streamlit-mark-color.svg" onerror="this.style.display='none'"/>
      <div class="td-tool-label">Streamlit</div>
    </div>
    <div class="td-tool">
      <img src="https://upload.wikimedia.org/wikipedia/commons/c/cf/New_Power_BI_Logo.svg" onerror="this.style.display='none'"/>
      <div class="td-tool-label">Power BI</div>
    </div>
    <div class="td-tool">
      <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/github/github-original.svg" style="filter:invert(1);" onerror="this.style.display='none'"/>
      <div class="td-tool-label">GitHub</div>
    </div>
    <div class="td-tool">
      <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/vscode/vscode-original.svg" onerror="this.style.display='none'"/>
      <div class="td-tool-label">VS Code</div>
    </div>
    <div class="td-tool">
      <img src="https://upload.wikimedia.org/wikipedia/commons/3/34/Microsoft_Office_Excel_%282019%E2%80%93present%29.svg" onerror="this.style.display='none'"/>
      <div class="td-tool-label">Excel</div>
    </div>
    <div class="td-tool">
      <img src="https://assets-global.website-files.com/6257adef93867e50d84d30e2/636e0a69f118df70ad7828d4_icon_clyde_blurple_RGB.svg" onerror="this.style.display='none'"/>
      <div class="td-tool-label">Discord</div>
    </div>
    <div class="td-tool">
      <img src="https://upload.wikimedia.org/wikipedia/commons/1/12/Google_Drive_icon_%282020%29.svg" onerror="this.style.display='none'"/>
      <div class="td-tool-label">Google Drive</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)
