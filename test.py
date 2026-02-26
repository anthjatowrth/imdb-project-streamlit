import pandas as pd
from src.utils import pick_poster_url, resolve_poster_url

df = pd.read_csv("data/output/10_final_imdb_tmdb.csv", sep=",")
# Récupère la ligne du film
row = df[df["ID"] == "tt26548265"].iloc[0]

# Étape 1 — ce que contiennent les colonnes poster
print("Poster1 brut :", row.get("Poster1"))
print("Poster2 brut :", row.get("Poster2"))

# Étape 2 — ce que resolve_poster_url en fait
print("Poster1 résolu :", resolve_poster_url(row.get("Poster1")))
print("Poster2 résolu :", resolve_poster_url(row.get("Poster2")))

# Étape 3 — ce que pick_poster_url retourne au final
print("URL finale :", pick_poster_url(row))