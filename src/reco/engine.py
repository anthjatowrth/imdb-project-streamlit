from __future__ import annotations

import re
from typing import Any

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix, hstack
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MultiLabelBinarizer, StandardScaler, normalize

GATED_COLS: tuple[str, ...] = ("is_animation", "is_documentary", "is_horror")


def parse_simple(x: Any) -> list[str]:
    if isinstance(x, list):
        return [str(v).strip() for v in x if str(v).strip()]
    s = str(x).strip()
    s = s.replace("[", "").replace("]", "")
    parts = [p.strip().strip("'").strip('"') for p in s.split(",")]
    return [p for p in parts if p]


def clean_txt(x: Any) -> str:
    s = str(x).lower()
    s = re.sub(r"[,\|;/]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def _add_gated_flags(df: pd.DataFrame) -> None:
    def has(token: str) -> pd.Series:
        t = clean_txt(token)
        return df["genres_list"].apply(lambda g: any(clean_txt(v) == t for v in g)).astype(bool)

    df["is_animation"] = has("Animation")
    df["is_documentary"] = has("Documentary")
    df["is_horror"] = has("Horror")


def _apply_gated_lock(cand: pd.DataFrame, ref_row: pd.Series) -> pd.DataFrame:
    out = cand
    for col in GATED_COLS:
        out = out[out[col]] if bool(ref_row[col]) else out[~out[col]]
    return out


def _post_filter(
    cand: pd.DataFrame,
    *,
    ref_row: pd.Series,
    year_min: int,
    year_max: int,
    min_rating: float | None,
    top_n: int,
    gated_lock: bool) -> pd.DataFrame:
    if gated_lock:
        cand = _apply_gated_lock(cand, ref_row)

    y = cand["Année_de_sortie"].astype(int)
    cand = cand[y.between(year_min, year_max)]

    if min_rating is not None:
        cand = cand[cand["Note_moyenne"].astype(float) >= float(min_rating)]

    cand = cand.sort_values("distance_cosine", ascending=True).head(int(top_n))

    cols = [
        "ID",
        "Titre",
        "Année_de_sortie",
        "Réalisateurs",
        "Note_moyenne",
        "Durée",
        "Genre",
        "Pays_origine",
        "distance_cosine"]
    
    other = [c for c in cand.columns if c not in cols]
    return (
        cand[cols + other]
        .drop(columns=list(GATED_COLS), errors="ignore")
        .reset_index(drop=True))

def _neighbors(
    artifacts: dict,
    *,
    ref_idx: int,
    top_n: int,
    candidate_k: int) -> pd.DataFrame:
    df: pd.DataFrame = artifacts["df"]
    X = artifacts["X"]
    model: NearestNeighbors = artifacts["model"]

    k = int(min(max(candidate_k, top_n + 50), X.shape[0]))
    distances, indices = model.kneighbors(X[ref_idx], n_neighbors=k)

    inds = indices.ravel()
    dists = distances.ravel()

    keep = inds != ref_idx
    cand = df.iloc[inds[keep]].copy()
    cand["distance_cosine"] = dists[keep]
    return cand


def build_artifacts(
    df_raw: pd.DataFrame,
    *,
    w_genre: float = 0.2,
    w_country: float = 0.25,
    w_sum: float = 0.3,
    w_cast: float = 0.1,
    w_dir: float = 0.2,
    w_num: float = 0.1,
    w_pop: float = 0.05,
    n_neighbors: int = 11) -> dict:
    df = df_raw.copy()
    df.columns = df.columns.str.strip()
    df = df.reset_index(drop=True) 

    df["txt_summary"] = df["Résumé"].map(clean_txt)
    df["txt_cast"] = df["Casting"].map(clean_txt)
    df["txt_director"] = df["Réalisateurs"].map(clean_txt)

    tfidf_common = dict(
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.85,
        strip_accents="unicode",
        stop_words="english",
        token_pattern=r"(?u)\b\w\w+\b",
        lowercase=False)

    tfidf_sum = TfidfVectorizer(**tfidf_common)
    tfidf_cast = TfidfVectorizer(**tfidf_common)
    tfidf_dir = TfidfVectorizer(**tfidf_common)

    X_sum = tfidf_sum.fit_transform(df["txt_summary"])
    X_cast = tfidf_cast.fit_transform(df["txt_cast"])
    X_dir = tfidf_dir.fit_transform(df["txt_director"])


    df["genres_list"] = df["Genre"].apply(parse_simple)
    df["countries_list"] = df["Pays_origine"].apply(parse_simple)
    df["pop_list"] = df["Popularité"].apply(parse_simple)

    _add_gated_flags(df)

    mlb_genre = MultiLabelBinarizer(sparse_output=True)
    mlb_country = MultiLabelBinarizer(sparse_output=True)
    mlb_pop = MultiLabelBinarizer(sparse_output=True)

    X_genre = mlb_genre.fit_transform(df["genres_list"])
    X_country = mlb_country.fit_transform(df["countries_list"])
    X_pop = mlb_pop.fit_transform(df["pop_list"])


    num_cols = ["Durée", "Année_de_sortie", "Note_moyenne"]
    scaler = StandardScaler()
    X_num = scaler.fit_transform(df[num_cols].to_numpy(dtype=float))


    X = hstack(
        [
            X_genre * w_genre,
            X_country * w_country,
            X_sum * w_sum,
            X_cast * w_cast,
            X_dir * w_dir,
            X_pop * w_pop,
            csr_matrix(X_num * w_num)], format="csr")
    
    X = normalize(X)

    model = NearestNeighbors(metric="cosine", n_neighbors=int(n_neighbors))
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
        "num_cols": num_cols}


def recommend(
    artifacts: dict,
    *,
    movie_id: Any | None = None,
    title_query: str | None = None,
    year: int | None = None,
    director_query: str | None = None,
    year_min: int = 1950,
    year_max: int = 2026,
    min_rating: float | None = None,
    top_n: int = 200,
    candidate_k: int = 1200,
    gated_lock: bool = True) -> pd.DataFrame:
    df: pd.DataFrame = artifacts["df"]

    if movie_id is not None:
        mask = df["ID"].astype(str).eq(str(movie_id)).to_numpy()
    else:
        t = str(title_query).strip().lower()
        mask = df["Titre"].astype(str).str.strip().str.lower().eq(t).to_numpy()

        if year is not None:
            mask = mask & (df["Année_de_sortie"].astype(int).to_numpy() == int(year))

        if director_query is not None:
            dq = clean_txt(director_query)
            mask = mask & df["txt_director"].str.contains(dq, regex=False).to_numpy()

    if not mask.any():
        return df.iloc[0:0].copy()

    ref_idx = int(np.flatnonzero(mask)[0])
    ref_row = df.iloc[ref_idx]

    cand = _neighbors(artifacts, ref_idx=ref_idx, top_n=top_n, candidate_k=candidate_k)

    return _post_filter(
        cand,
        ref_row=ref_row,
        year_min=year_min,
        year_max=year_max,
        min_rating=min_rating,
        top_n=top_n,
        gated_lock=gated_lock,
    )