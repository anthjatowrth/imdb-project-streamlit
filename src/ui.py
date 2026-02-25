import streamlit as st
from typing import Callable

def render_sidebar(*, extra: Callable[[], None] | None = None) -> None:
    st.markdown(
        """
        <style>
        /* Remonte la sidebar */
        section[data-testid="stSidebar"] > div {
            padding-top: 0rem;
            margin-top: -3rem;
        }

        /* Boutons de navigation (look "cards") */
        section[data-testid="stSidebar"] div[data-testid="stButton"] > button {
            width: 100%;
            padding: 1.05rem 1.15rem;      /* garde tes gros encarts */
            font-size: 1.15rem;            /* police + grosse */
            font-weight: 650;
            letter-spacing: 0.2px;

            border-radius: 0.90rem;
            border: 1px solid rgba(255,255,255,0.10);

            /* Fond translucent + dégradé très léger */
            background: linear-gradient(
                180deg,
                rgba(255,255,255,0.06),
                rgba(255,255,255,0.03)
            );

            /* Effet verre discret */
            backdrop-filter: blur(8px);

            /* Ombre douce */
            box-shadow:
                0 10px 24px rgba(0,0,0,0.25),
                inset 0 1px 0 rgba(255,255,255,0.06);

            transition: transform 140ms ease, box-shadow 140ms ease, border-color 140ms ease, background 140ms ease;
        }

        section[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover {
            transform: translateY(-1px);
            border-color: rgba(255,255,255,0.18);
            background: linear-gradient(
                180deg,
                rgba(255,255,255,0.075),
                rgba(255,255,255,0.035)
            );
            box-shadow:
                0 14px 30px rgba(0,0,0,0.32),
                inset 0 1px 0 rgba(255,255,255,0.08);
        }

        section[data-testid="stSidebar"] div[data-testid="stButton"] > button:active {
            transform: translateY(0px) scale(0.99);
        }

        /* Espace vertical entre les encarts */
        section[data-testid="stSidebar"] div[data-testid="stButton"] {
            margin-bottom: 0.75rem;
        }

        /* Optionnel : rendre les dividers plus discrets */
        section[data-testid="stSidebar"] hr {
            border-color: rgba(255,255,255,0.08);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

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