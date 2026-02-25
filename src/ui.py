import streamlit as st
from typing import Any, Callable


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

def render_sidebar(*, extra: Callable[[], None] | None = None) -> None:
    with st.sidebar:
        st.image("assets/logo_noir.png")
        st.divider()

        if st.button("Accueil", use_container_width=True):
            st.switch_page("app.py")

        if st.button("Catalogue", use_container_width=True):
            st.switch_page("pages/Catalogue.py")

        if st.button("Recommandations", use_container_width=True):
            st.switch_page("pages/Reco_ML.py")

        st.divider()

        if extra is not None:
            extra()
