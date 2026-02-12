from src.config import *
import numpy as np
import pandas as pd
import re
from scipy.sparse import hstack, csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler, normalize
from sklearn.neighbors import NearestNeighbors

df = pd.read_csv(OUTPUT_DIR / "10_final_imdb_tmdb.csv", sep=",")

txt_cols = ["Genre", "Réalisateurs", "Casting", "Pays_origine", "Boite_de_production", "Résumé", "Accroche"]
for c in txt_cols:
    df[c] = df[c].fillna("").astype(str)

df["txt"] = df[txt_cols].agg(" ".join, axis=1)

def clean_txt(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[,\|;/]+", " ", s)  
    s = re.sub(r"\s+", " ", s).strip()
    return s

df["txt"] = df["txt"].map(clean_txt)


vectorizer = TfidfVectorizer(
    token_pattern=r"(?u)\b\w+\b",  
    ngram_range=(1, 2),            
    min_df=2,                      
    max_df=0.85,                   
    strip_accents="unicode"        
)
X_text = vectorizer.fit_transform(df["txt"])


num_cols = ["Année_de_sortie", "Durée", "Note_moyenne", "Nombre_votes"]
df[num_cols] = df[num_cols].apply(pd.to_numeric, errors="coerce").fillna(0)


df["Nombre_votes"] = np.log1p(df["Nombre_votes"])

scaler = StandardScaler(with_mean=True, with_std=True)
X_num = scaler.fit_transform(df[num_cols].values) 

alpha = 0.7 
X_text_w = X_text * alpha
X_num_w = csr_matrix(X_num * (1 - alpha))  

X = hstack([X_text_w, X_num_w], format="csr")

X = normalize(X)

model = NearestNeighbors(metric="cosine", n_neighbors=11)
model.fit(X)


mask = (df["Titre"] == "Titanic") & (df["Année_de_sortie"] == 1997)
idx = df.index[mask][0]

distances, indices = model.kneighbors(X[idx], n_neighbors=11)

reco_idx = indices[0][1:]
reco_dist = distances[0][1:]

reco = df.loc[reco_idx, ["Titre", "Année_de_sortie"]].copy()
reco["distance_cosine"] = reco_dist
print(reco)

print("Distances :", np.round(reco_dist, 3))



# Algo de CHATGPT pour savoir si la distribution des recommandations semble correcte :

# sample_idx = np.random.choice(len(df), size=200, replace=False)
# all_d = []
# for i in sample_idx:
#     d, _ = model.kneighbors(X[i], n_neighbors=11)
#     all_d.extend(d[0][1:])
# print("Percentiles:", np.round(np.percentile(all_d, [5,25,50,75,95]), 4))