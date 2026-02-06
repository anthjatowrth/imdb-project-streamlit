import streamlit as st

st.title("Projet Cinéma Creuse")
st.write("Ici, *On trouve votre prochain film préféré !* :sunglasses:")
st.date_input("Date du jour", "today")

year_min, year_max = st.slider("Sélectionne une période", min_value=1950, max_value=2025, value=(1980, 2020), step=1)
st.write(f"Période sélectionnée : {year_min} – {year_max}")

real = st.text_input("Qui est votre réalisateur préféré ?")

st.write(f"Vous avez choisi : {real}.")
