import streamlit as st
from typing import Any, Callable
from pathlib import Path
import base64


# ── Helpers partagés ──────────────────────────────────────────────────────────

def clip_text(s: Any, max_len: int = 34) -> str:
    """Tronque un texte avec ellipse si trop long."""
    txt = str(s) if s is not None else ""
    txt = txt.strip()
    if not txt or txt.lower() == "nan":
        return "—"
    if len(txt) <= max_len:
        return txt
    return txt[: max_len - 1].rstrip() + "…"


def fmt_votes(v: Any) -> str:
    """Formate un nombre de votes avec séparateurs d'espaces."""
    try:
        return f"{int(float(v)):,}".replace(",", " ")
    except Exception:
        return "—"


# ── Sidebar ───────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def _img_to_b64(path: str) -> str:
    return base64.b64encode(Path(path).read_bytes()).decode("utf-8")

def render_sidebar(*, extra: Callable[[], None] | None = None) -> None:
    # Injection du logo en base64 dans le CSS de la sidebar
    try:
        b64 = _img_to_b64("assets/logo_rotate.png")
        st.markdown(
            f"""
            <style>
            [data-testid="stSidebar"] {{
                position: relative;
                overflow: hidden;
                background: var(--grad-dark) !important;
            }}
            /* couche floutée */
            [data-testid="stSidebar"]::before {{
                content: "";
                position: absolute;
                inset: 0;
                z-index: 0;
                background:
                    linear-gradient(180deg,
                        rgba(15,14,26,0.96) 0%,
                        rgba(15,14,26,0.70) 30%,
                        rgba(15,14,26,0.70) 70%,
                        rgba(15,14,26,0.96) 100%
                    ),
                    url("data:image/png;base64,{b64}") center / 300px no-repeat;
                filter: blur(13px);
                opacity: 0.9;
                transform: scale(1.1);
            }}
            /* contenu au dessus */
            [data-testid="stSidebar"] > div {{
                position: relative;
                z-index: 1;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
    except Exception:
        pass

    with st.sidebar:

        # ── Branding header ───────────────────────────────────────────────────
        st.markdown(
            """
            <div style="text-align:center; padding: 1.4rem 0.5rem 0.8rem 0.5rem;">
                <div style="
                    font-family: 'Bebas Neue', Impact, sans-serif;
                    letter-spacing: 0.12em;
                    text-transform: uppercase;
                    filter: drop-shadow(0 0 8px rgba(255,200,0,0.55)) drop-shadow(0 0 22px rgba(255,170,0,0.3));
                    line-height: 1;
                ">
                    <span style="color: #FFD700; font-size: 1.85rem;">Ciné</span><span style="color: #ffffff; font-size: 1.85rem;">Data</span>
                </div>
                <div style="
                    color: rgba(200,200,220,0.55);
                    font-size: 0.68rem;
                    letter-spacing: 0.18em;
                    text-transform: uppercase;
                    margin-top: 0.3rem;
                ">
                    🎬 &nbsp; ton cinéma, ta data
                </div>
                <div style="
                    width: 80%;
                    height: 1px;
                    margin: 0.75rem auto 0;
                    background: linear-gradient(90deg, transparent, #FFD700, transparent);
                    box-shadow: 0 0 10px rgba(255,210,0,0.5);
                "></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("Accueil", use_container_width=True):
            st.switch_page("app.py")
        if st.button("Catalogue", use_container_width=True):
            st.switch_page("pages/Catalogue.py")
        if st.button("Recommandations", use_container_width=True):
            st.switch_page("pages/Reco_ML.py")
        st.divider()
        if extra is not None:
            extra()