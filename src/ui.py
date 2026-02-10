import streamlit as st

def render_sidebar():
    st.sidebar.markdown(
        """
        <style>
        div[data-testid="stSidebar"] button {
            width: 100%;
            padding: 0.75rem 1rem;
            font-size: 1.05rem;
            font-weight: 600;
            border-radius: 0.75rem;} </style> """, unsafe_allow_html=True)

    st.sidebar.title("🎬 IMDB Reco")

    if st.sidebar.button("🏠 Accueil", use_container_width=True):
        st.switch_page("app.py")

    if st.sidebar.button("👤 Espace client", use_container_width=True):
        st.switch_page("pages/2_👤_Espace_client.py")

    if st.sidebar.button("🎬 Catalogue", use_container_width=True):
        st.switch_page("pages/3_🎬_Catalogue.py")

    if st.sidebar.button("✨ Recommandations", use_container_width=True):
        st.switch_page("pages/4_✨_Recommandations.py")

    st.sidebar.divider()

 