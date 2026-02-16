from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from typing import Any, Optional

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix, hstack
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MultiLabelBinarizer, StandardScaler, normalize


def _parse_genres(s: Any) -> list[str]:
    if pd.isna(s) or str(s).strip() == "":
        return []
    return [g.strip().lower() for g in str(s).split(",") if g.strip()]


def _parse_countries(s: Any) -> list[str]:
    if pd.isna(s) or str(s).strip() == "":
        return []
    try:
        lst = ast.literal_eval(str(s))
        if isinstance(lst, list):
            return [str(c).strip().lower() for c in lst if str(c).strip()]
        return []
    except Exception:
        return [c.strip().lower() for c in str(s).replace(";", ",").split(",") if c.strip()]


def _clean_txt(s: Any) -> str:
    s = "" if s is None else str(s)
    s = s.lower()
    s = re.sub(r"[,\|;/]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _to_numeric(series: pd.Series, default: float = 0.0) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").fillna(default)


def _year_in_range(series: pd.Series, y_min: int, y_max: int) -> pd.Series:
    y = _to_numeric(series, default=0).astype(int)
    return y.between(int(y_min), int(y_max), inclusive="both")


def _rating_at_least(series: pd.Series, min_rating: float) -> pd.Series:
    r = _to_numeric(series, default=np.nan)
    return r.ge(float(min_rating))


def _pick_rating_col(df: pd.DataFrame) -> Optional[str]:
    """
    Ton dataset semble avoir "Note_moyenne". On garde ça en priorité,
    mais on met des fallbacks si un jour tu changes de source.
    """
    preferred = [
        "Note_moyenne",
        "vote_average",
        "averageRating",
        "rating",
        "note",
        "Note",
    ]
    for c in preferred:
        if c in df.columns:
            return c

    for c in df.columns:
        cl = c.lower()
        if "note" in cl or "rating" in cl or "vote" in cl:
            return c

    return None



@dataclass(frozen=True)
class RecoArtifacts:
    df: pd.DataFrame
    X: csr_matrix
    rating_col: Optional[str]


def build_artifacts(df: pd.DataFrame) -> dict:
    """
    Prépare les features + matrice normalisée X.
    Retourne un dict pour être utilisé comme artifacts["df"] dans ton app.
    """
    df = df.copy()
    df.columns = df.columns.str.strip()

    for c in ["Résumé", "Casting", "Réalisateurs", "Producteurs"]:
        if c not in df.columns:
            df[c] = ""
        df[c] = df[c].fillna("").astype(str)

    df["txt_summary"] = df["Résumé"].map(_clean_txt)
    df["txt_cast"] = df["Casting"].map(_clean_txt)
    df["txt_director"] = df["Réalisateurs"].map(_clean_txt)
    df["txt_productor"] = df["Producteurs"].map(_clean_txt)

    tfidf_sum = TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.85,
        strip_accents="unicode",
        stop_words="english",
        lowercase=True,
        token_pattern=r"(?u)\b\w\w+\b",
    )
    X_sum = tfidf_sum.fit_transform(df["txt_summary"])

    tfidf_cast = TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.85,
        strip_accents="unicode",
        stop_words="english",
        lowercase=True,
        token_pattern=r"(?u)\b\w\w+\b",
    )
    X_cast = tfidf_cast.fit_transform(df["txt_cast"])

    tfidf_dir = TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.85,
        strip_accents="unicode",
        stop_words="english",
        lowercase=True,
        token_pattern=r"(?u)\b\w\w+\b",
    )
    X_dir = tfidf_dir.fit_transform(df["txt_director"])

    if "Genre" not in df.columns:
        df["Genre"] = ""
    if "Pays_origine" not in df.columns:
        df["Pays_origine"] = ""

    df["genres_list"] = df["Genre"].fillna("").apply(_parse_genres)
    df["countries_list"] = df["Pays_origine"].fillna("").apply(_parse_countries)

    mlb_genre = MultiLabelBinarizer(sparse_output=True)
    mlb_country = MultiLabelBinarizer(sparse_output=True)
    X_genre = mlb_genre.fit_transform(df["genres_list"])
    X_country = mlb_country.fit_transform(df["countries_list"])

    num_cols = ["Durée", "Année_de_sortie"]
    for c in num_cols:
        if c not in df.columns:
            df[c] = 0

    df["Durée"] = _to_numeric(df["Durée"], default=0.0)
    df["Année_de_sortie"] = _to_numeric(df["Année_de_sortie"], default=0.0).astype(int)

    scaler = StandardScaler(with_mean=True, with_std=True)
    X_num = scaler.fit_transform(df[num_cols].values)


    w_genre = 0.1
    w_country = 0.1
    w_sum = 0.1
    w_cast = 0.1
    w_dir = 0.1
    w_num = 0.1

    X = hstack(
        [
            X_genre * w_genre,
            X_country * w_country,
            X_sum * w_sum,
            X_cast * w_cast,
            X_dir * w_dir,
            csr_matrix(X_num * w_num),
        ],
        format="csr",
    )

   
    X = normalize(X)

    rating_col = _pick_rating_col(df)

    art = RecoArtifacts(df=df, X=X, rating_col=rating_col)

 
    return {"df": df, "art": art}


def recommend(
    artifacts: dict,
    title_query: str,
    year_min: int = 1950,
    year_max: int = 2025,
    min_rating: Optional[float] = None,
    top_n: int = 50,
    candidate_k: int = 1200,  # gardé pour compat UI, pas indispensable avec la méthode dot-product
) -> pd.DataFrame:
    """
    Applique les filtres UI (année + note min) sur le pool candidat,
    puis calcule les top_n plus proches (cosine) via dot-product (X normalisé).

    Retourne un df trié, prêt à paginer côté Streamlit.
    """
    art: RecoArtifacts = artifacts["art"]
    df = art.df
    X = art.X

    if "Titre" not in df.columns:
        raise ValueError("Colonne 'Titre' absente du dataframe.")


    mask_q = df["Titre"].astype(str).str.strip().str.lower().eq(title_query.strip().lower())
    if not mask_q.any():
        raise ValueError(f"Aucun film trouvé pour: {title_query}")

    idx = df.index[mask_q][0]

  
    mask = _year_in_range(df["Année_de_sortie"], year_min, year_max) & (df.index != idx)

    if (min_rating is not None) and (float(min_rating) > 0):
        if art.rating_col is None:
            raise ValueError(
                "Aucune colonne de note détectée dans le dataset. "
                "Ajoute une colonne de note ou adapte _pick_rating_col()."
            )
        mask = mask & _rating_at_least(df[art.rating_col], float(min_rating))

    candidate_idx = df.index[mask]
    if len(candidate_idx) == 0:
        msg = f"Aucun film candidat entre {year_min}-{year_max}"
        if min_rating is not None and float(min_rating) > 0:
            msg += f" avec note >= {min_rating}"
        raise ValueError(msg + ".")

 
    q = X[idx]             
    C = X[candidate_idx]       

  
    similarities = (q @ C.T).toarray().ravel()
    distances = 1.0 - similarities

    k = int(top_n)
    k = max(1, min(k, len(candidate_idx)))

    best_pos = np.argpartition(distances, kth=k - 1)[:k]
    best_pos = best_pos[np.argsort(distances[best_pos])]

    reco_idx = candidate_idx[best_pos]
    reco_dist = distances[best_pos]
    reco_sim = 1.0 - reco_dist

  
    cols = ["Titre", "Année_de_sortie", "Genre", "Pays_origine"]
    if art.rating_col is not None and art.rating_col in df.columns:
        cols = cols + [art.rating_col]

    reco = df.loc[reco_idx, cols].copy()
    reco["distance_cosine"] = reco_dist
    reco["similarity_cosine"] = reco_sim

  
    reco = reco.sort_values("distance_cosine", ascending=True).reset_index(drop=True)
    return reco