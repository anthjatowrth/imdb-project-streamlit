from __future__ import annotations

import re
from typing import Any

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix, hstack
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MultiLabelBinarizer, StandardScaler, normalize


def parse_simple(s: Any) -> list[str]:
    """Parse une chaîne type "['France', 'USA']" ou "France, USA" en liste.
    Robuste aux NaN/float/None.
    """
    if s is None or (isinstance(s, float) and np.isnan(s)):
        return []
    s = str(s).strip()
    if not s:
        return []
    s = s.replace("[", "").replace("]", "")
    parts = [p.strip().strip("'").strip('"') for p in s.split(",")]
    return [p for p in parts if p]


def clean_txt(s: Any) -> str:
    s = "" if s is None or (isinstance(s, float) and np.isnan(s)) else str(s)
    s = s.lower()
    s = re.sub(r"[,\|;/]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def build_artifacts(
    df_raw: pd.DataFrame,
    *,

    w_genre: float = 0.4,
    w_country: float = 0.1,
    w_sum: float = 0.4,
    w_cast: float = 0.1,
    w_dir: float = 0.2,
    w_num: float = 0.1,
    w_pop: float = 0.1,
    n_neighbors: int = 11,
) -> dict:
    df = df_raw.copy()
    df.columns = df.columns.str.strip()

    for c in ["Résumé", "Casting", "Réalisateurs", "Producteurs"]:
        if c not in df.columns:
            df[c] = ""
        df[c] = df[c].fillna("").astype(str)

    df["txt_summary"] = df["Résumé"].map(clean_txt)
    df["txt_cast"] = df["Casting"].map(clean_txt)
    df["txt_director"] = df["Réalisateurs"].map(clean_txt)
    df["txt_productor"] = df["Producteurs"].map(clean_txt)

    tfidf_common = dict(
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.85,
        strip_accents="unicode",
        stop_words="english",
        lowercase=True,
        token_pattern=r"(?u)\b\w\w+\b",
    )

    tfidf_sum = TfidfVectorizer(**tfidf_common)
    X_sum = tfidf_sum.fit_transform(df["txt_summary"])

    tfidf_cast = TfidfVectorizer(**tfidf_common)
    X_cast = tfidf_cast.fit_transform(df["txt_cast"])

    tfidf_dir = TfidfVectorizer(**tfidf_common)
    X_dir = tfidf_dir.fit_transform(df["txt_director"])

    if "Genre" not in df.columns:
        df["Genre"] = ""
    if "Pays_origine" not in df.columns:
        df["Pays_origine"] = ""
    if "Popularité" not in df.columns:
        df["Popularité"] = ""

    df["genres_list"] = df["Genre"].apply(parse_simple)
    df["countries_list"] = df["Pays_origine"].apply(parse_simple)
    df["pop_list"] = df["Popularité"].apply(parse_simple)

    mlb_genre = MultiLabelBinarizer(sparse_output=True)
    mlb_country = MultiLabelBinarizer(sparse_output=True)
    mlb_pop = MultiLabelBinarizer(sparse_output=True)

    X_genre = mlb_genre.fit_transform(df["genres_list"])
    X_country = mlb_country.fit_transform(df["countries_list"])
    X_pop = mlb_pop.fit_transform(df["pop_list"])

    num_cols = ["Durée", "Année_de_sortie", "Note_moyenne"]
    for c in num_cols:
        if c not in df.columns:
            df[c] = 0
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    scaler = StandardScaler(with_mean=True, with_std=True)
    X_num = scaler.fit_transform(df[num_cols].values)

    X_genre_n = normalize(X_genre)
    X_country_n = normalize(X_country)
    X_sum_n = normalize(X_sum)
    X_cast_n = normalize(X_cast)
    X_dir_n = normalize(X_dir)
    X_pop_n = normalize(X_pop)

    X = hstack([
            X_genre_n * w_genre,
            X_country_n * w_country,
            X_sum_n * w_sum,
            X_cast_n * w_cast,
            X_dir_n * w_dir,
            X_pop_n * w_pop,
            csr_matrix(X_num * w_num),], format="csr")
    
    X = normalize(X)

    model = NearestNeighbors(metric="cosine", n_neighbors=n_neighbors)
    model.fit(X)

    return {
        "df": df,
        "X": X,
        "model": model,
        "tfidf_sum": tfidf_sum,
        "tfidf_cast": tfidf_cast,
        "tfidf_dir": tfidf_dir,
        "mlb_genre": mlb_genre,
        "mlb_country": mlb_country,
        "mlb_pop": mlb_pop,
        "scaler": scaler,
        "num_cols": num_cols,
        "weights": {
            "w_genre": w_genre,
            "w_country": w_country,
            "w_sum": w_sum,
            "w_cast": w_cast,
            "w_dir": w_dir,
            "w_num": w_num,
            "w_pop": w_pop,
        },
    }


def recommend(
    artifacts: dict,
    *,
    title_query: str,
    year_min: int = 1950,
    year_max: int = 2025,
    min_rating: float | None = None,
    top_n: int = 200,
    candidate_k: int = 1200,
) -> pd.DataFrame:
    df: pd.DataFrame = artifacts["df"]
    X = artifacts["X"]
    model: NearestNeighbors = artifacts["model"]

    t = str(title_query).strip().lower()
    mask = df["Titre"].astype(str).str.strip().str.lower().eq(t)
    if not mask.any():
        raise ValueError("Titre introuvable dans la base.")

    ref_idx = int(np.flatnonzero(mask.values)[0])

    k = int(min(max(candidate_k, top_n + 50), X.shape[0]))
    distances, indices = model.kneighbors(X[ref_idx], n_neighbors=k)

    inds = indices.ravel().tolist()
    dists = distances.ravel().tolist()

    pairs = [(i, d) for i, d in zip(inds, dists) if i != ref_idx]

    cand = df.iloc[[i for i, _ in pairs]].copy()
    cand["distance_cosine"] = [d for _, d in pairs]


    if "Année_de_sortie" in cand.columns:
        cand = cand[(cand["Année_de_sortie"] >= year_min) & (cand["Année_de_sortie"] <= year_max)]

    if min_rating is not None and "Note_moyenne" in cand.columns:
        cand = cand[cand["Note_moyenne"] >= float(min_rating)]

    cand = cand.sort_values("distance_cosine", ascending=True).head(int(top_n))

    preferred_cols = [
        "Titre",
        "Année_de_sortie",
        "Note_moyenne",
        "Durée",
        "Genre",
        "Pays_origine",
        "distance_cosine",
    ]
    cols = [c for c in preferred_cols if c in cand.columns]
    other = [c for c in cand.columns if c not in cols]
    cand = cand[cols + other]

    return cand.reset_index(drop=True)
