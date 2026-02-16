import ast
import re
import numpy as np
import pandas as pd

from scipy.sparse import hstack, csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MultiLabelBinarizer, StandardScaler, normalize
from sklearn.neighbors import NearestNeighbors
from src.config import *


df = pd.read_csv(OUTPUT_DIR / "10_final_imdb_tmdb.csv", sep=",")
df.columns = df.columns.str.strip()


def parse_genres(s: str) -> list[str]:
    if pd.isna(s) or str(s).strip() == "":
        return []
    return [g.strip().lower() for g in str(s).split(",") if g.strip()]

def parse_countries(s: str) -> list[str]:
    if pd.isna(s) or str(s).strip() == "":
        return []
    try:
        lst = ast.literal_eval(str(s))
        if isinstance(lst, list):
            return [str(c).strip().lower() for c in lst if str(c).strip()]
        return []
    except Exception:
        return [c.strip().lower() for c in str(s).replace(";", ",").split(",") if c.strip()]


def clean_txt(s: str) -> str:
    s = "" if s is None else str(s)
    s = s.lower()
    s = re.sub(r"[,\|;/]+", " ", s)    
    s = re.sub(r"\s+", " ", s).strip()
    return s

for c in ["Résumé", "Casting", "Réalisateurs", "Producteurs"]:
    df[c] = df[c].fillna("").astype(str)

df["txt_summary"]  = df["Résumé"].map(clean_txt)
df["txt_cast"]     = df["Casting"].map(clean_txt)
df["txt_director"] = df["Réalisateurs"].map(clean_txt)
df["txt_productor"] = df["Producteurs"].map(clean_txt)


tfidf = TfidfVectorizer(
    ngram_range=(1, 2),
    min_df=2,
    max_df=0.85,
    strip_accents="unicode",
    stop_words="english",        
    lowercase=True,
    token_pattern=r"(?u)\b\w\w+\b")


X_sum  = tfidf.fit_transform(df["txt_summary"])

tfidf_cast = TfidfVectorizer(
    ngram_range=(1, 2),
    min_df=2,
    max_df=0.85,
    strip_accents="unicode",
    stop_words="english",
    lowercase=True,
    token_pattern=r"(?u)\b\w\w+\b")

X_cast = tfidf_cast.fit_transform(df["txt_cast"])

tfidf_dir = TfidfVectorizer(
    ngram_range=(1, 2),
    min_df=2,
    max_df=0.85,
    strip_accents="unicode",
    stop_words="english",
    lowercase=True,
    token_pattern=r"(?u)\b\w\w+\b")

X_dir  = tfidf_dir.fit_transform(df["txt_director"])


df["genres_list"] = df["Genre"].fillna("").apply(parse_genres)
df["countries_list"] = df["Pays_origine"].fillna("").apply(parse_countries)

mlb_genre = MultiLabelBinarizer(sparse_output=True)
mlb_country = MultiLabelBinarizer(sparse_output=True)

X_genre = mlb_genre.fit_transform(df["genres_list"])
X_country = mlb_country.fit_transform(df["countries_list"])


num_cols = ["Durée", "Année_de_sortie"]
for c in num_cols:
    df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

scaler = StandardScaler(with_mean=True, with_std=True)
X_num = scaler.fit_transform(df[num_cols].values)


w_genre   = 0.1
w_country = 0.1
w_sum     = 0.1
w_cast    = 0.1
w_dir     = 0.1
w_num     = 0.1

X = hstack([
    X_genre   * w_genre,
    X_country * w_country,
    X_sum     * w_sum,
    X_cast    * w_cast,
    X_dir     * w_dir,
    csr_matrix(X_num * w_num),
], format="csr")


X = normalize(X) 



model = NearestNeighbors(metric="cosine", n_neighbors=11)
model.fit(X)


# ---------------------------
# FILTERS (test bounds)
# ---------------------------
YEAR_MIN = 2000
YEAR_MAX = 2010

RATING_COL = "Note_moyenne"   # <-- A MODIFIER : ex "averageRating", "vote_average", "Rating", etc.
MIN_RATING = 7.5      # note minimale (ex: 7.0/10)


def year_in_range(series: pd.Series, y_min: int, y_max: int) -> pd.Series:
    y = pd.to_numeric(series, errors="coerce")
    return y.between(y_min, y_max, inclusive="both")


def rating_at_least(series: pd.Series, min_rating: float) -> pd.Series:
    r = pd.to_numeric(series, errors="coerce")
    return r.ge(min_rating)


# ---------------------------
# TEST QUERY
# ---------------------------
title_query = "Titanic"

mask_q = df["Titre"].astype(str).str.strip().str.lower().eq(title_query.strip().lower())
if not mask_q.any():
    raise ValueError(f"Aucun film trouvé pour: {title_query}")

idx = df.index[mask_q][0]

# 1) filtres candidats
mask_year = year_in_range(df["Année_de_sortie"], YEAR_MIN, YEAR_MAX)

if RATING_COL not in df.columns:
    raise ValueError(
        f"Colonne note introuvable: {RATING_COL}. "
        f"Colonnes dispo (extrait) : {list(df.columns)[:30]}"
    )

mask_rating = rating_at_least(df[RATING_COL], MIN_RATING)

candidate_idx = df.index[mask_year & mask_rating & (df.index != idx)]

if len(candidate_idx) == 0:
    raise ValueError(
        f"Aucun film candidat avec année {YEAR_MIN}-{YEAR_MAX} et note >= {MIN_RATING}."
    )

# 2) distance cosine vers tous les candidats, puis top-k
q = X[idx]            # (1, n_features)
C = X[candidate_idx]  # (n_candidates, n_features)

# X est normalisé => cosine distance = 1 - dot_product
similarities = (q @ C.T).toarray().ravel()
distances = 1.0 - similarities

k = 10
k = min(k, len(candidate_idx))

best_pos = np.argpartition(distances, kth=k-1)[:k]
best_pos = best_pos[np.argsort(distances[best_pos])]

reco_idx = candidate_idx[best_pos]
reco_dist = distances[best_pos]

reco = df.loc[reco_idx, ["Titre", "Année_de_sortie", "Genre", "Pays_origine", RATING_COL]].copy()
reco["distance_cosine"] = reco_dist
reco["similarity_cosine"] = 1 - reco["distance_cosine"]

print(reco)


#TEST DISTANCE COSINE PERCENTILE#

# sample_size = min(500, X.shape[0]) 
# sample_idx = np.random.choice(X.shape[0], sample_size, replace=False)

# all_distances = []

# for i in sample_idx:
#     d, _ = model.kneighbors(X[i], n_neighbors=11)
#     all_distances.extend(d[0][1:]) 

# print(np.percentile(all_distances, [5, 25, 50, 75, 95]))