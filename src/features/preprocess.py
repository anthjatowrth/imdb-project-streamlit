from src.config import *
import numpy as np
import pandas as pd
from scipy.sparse import hstack, csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler, normalize
from sklearn.neighbors import NearestNeighbors

df = pd.read_csv(OUTPUT_DIR / "10_final_imdb_tmdb.csv", sep=",")

# features qualitatives :
txt_cols = ["Genre", "Réalisateurs", "Casting", "Pays_origine", "Boite_de_production", "Résumé","Accroche"]
for c in txt_cols:
    df[c] = df[c].fillna("").astype(str)

df["txt"] = df[txt_cols].agg(" ".join, axis=1)

vectorizer = TfidfVectorizer(token_pattern=r"[^ ]+")
X_text = vectorizer.fit_transform(df["txt"])

# features numériques :
num_cols = ["Année_de_sortie", "Durée", "Note_moyenne", "Nombre_votes"]
df[num_cols] = df[num_cols].apply(pd.to_numeric, errors="coerce").fillna(0)

scaler = StandardScaler(with_mean=False)  
X_num = scaler.fit_transform(df[num_cols].values) 

# pondération
alpha = 0.80  
X_text_w = X_text * alpha
X_num_w = csr_matrix(X_num * (1 - alpha))

#concat
X = hstack([X_text_w, X_num_w], format="csr")


X = normalize(X)
model = NearestNeighbors(metric="cosine", n_neighbors=11)
model.fit(X)

#query  + reco
mask = (df["Titre"] == "Titanic") & (df["Année_de_sortie"] == 1997)
idx = df.index[mask][0]

distances, indices = model.kneighbors(X[idx], n_neighbors=11)

reco_idx = indices[0][1:]
reco_dist = distances[0][1:]

reco = df.loc[reco_idx, ["Titre", "Année_de_sortie", "Durée", "Note_moyenne", "Nombre_votes"]].copy()
reco["distance_cosine"] = reco_dist
print(reco)