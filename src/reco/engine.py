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


def has_genre_token(genres: Any, token: str) -> bool:
    """
    True si `token` est présent dans la liste de genres d'un film.
    Gère: liste python, "['Animation', 'Action']", "Animation, Action", etc.
    Match exact sur le token normalisé (évite faux positifs).
    """
    tok = clean_txt(token)

    if genres is None or (isinstance(genres, float) and np.isnan(genres)):
        return False

    if isinstance(genres, list):
        return any(clean_txt(g) == tok for g in genres)

    lst = parse_simple(genres)
    return any(clean_txt(g) == tok for g in lst)


def build_genre_flags(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ajoute des colonnes booléennes pour certains genres "gated".
    Colonnes ajoutées:
      - is_animation
      - is_documentary
      - is_horror
    """

    src = "genres_list" if "genres_list" in df.columns else "Genre"

    def _flag(token: str) -> pd.Series:
        return df[src].apply(lambda g: has_genre_token(g, token)).astype(bool)

    df["is_animation"] = _flag("Animation")
    df["is_documentary"] = _flag("Documentary")
    df["is_horror"] = _flag("Horror")
    return df


def apply_gated_genre_lock(
    cand: pd.DataFrame,
    *,
    ref_row: pd.Series,
    gated: tuple[str, ...] = ("is_animation", "is_documentary", "is_horror"),
) -> pd.DataFrame:
    """
    Applique la règle:
      - si le film de référence a le genre gated -> ne garder que les candidats qui l'ont
      - sinon -> exclure les candidats qui l'ont
    """
    out = cand
    for col in gated:
        if col not in out.columns or col not in ref_row.index:
            continue
        ref_has = bool(ref_row[col])
        if ref_has:
            out = out[out[col] == True]
        else:
            out = out[out[col] == False]
    return out


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
    n_neighbors: int = 11,
) -> dict:
    df = df_raw.copy()
    df.columns = df.columns.str.strip()

    if "ID" not in df.columns:
        raise ValueError("Colonne 'ID' introuvable : elle est requise pour éviter les homonymes.")

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


    df = build_genre_flags(df)

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

    X = hstack(
        [
            normalize(X_genre) * w_genre,
            normalize(X_country) * w_country,
            normalize(X_sum) * w_sum,
            normalize(X_cast) * w_cast,
            normalize(X_dir) * w_dir,
            normalize(X_pop) * w_pop,
            csr_matrix(X_num * w_num),
        ],
        format="csr",
    )

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
        "gated_genres": ("is_animation", "is_documentary", "is_horror"),
    }


def recommend_by_id(
    artifacts: dict,
    *,
    movie_id: Any,
    year_min: int = 1950,
    year_max: int = 2026,
    min_rating: float | None = None,
    top_n: int = 200,
    candidate_k: int = 1200,
    gated_lock: bool = True,
) -> pd.DataFrame:
    """Recommande à partir d'un ID unique (évite totalement le problème d'homonymes)."""
    df: pd.DataFrame = artifacts["df"]
    X = artifacts["X"]
    model: NearestNeighbors = artifacts["model"]

    mask = df["ID"].astype(str).eq(str(movie_id))
    if not mask.any():
        raise ValueError("ID introuvable dans la base.")

    ref_idx = int(np.flatnonzero(mask.values)[0])
    ref_row = df.iloc[ref_idx]

    k = int(min(max(candidate_k, top_n + 50), X.shape[0]))
    distances, indices = model.kneighbors(X[ref_idx], n_neighbors=k)

    inds = indices.ravel().tolist()
    dists = distances.ravel().tolist()

    pairs = [(i, d) for i, d in zip(inds, dists) if i != ref_idx]

    cand = df.iloc[[i for i, _ in pairs]].copy()
    cand["distance_cosine"] = [d for _, d in pairs]

    if gated_lock:
        gated = artifacts.get("gated_genres", ("is_animation", "is_documentary", "is_horror"))
        cand = apply_gated_genre_lock(cand, ref_row=ref_row, gated=tuple(gated))

    if "Année_de_sortie" in cand.columns:
        cand["Année_de_sortie"] = pd.to_numeric(cand["Année_de_sortie"], errors="coerce").fillna(0).astype(int)
        cand = cand[(cand["Année_de_sortie"] >= int(year_min)) & (cand["Année_de_sortie"] <= int(year_max))]

    if min_rating is not None and "Note_moyenne" in cand.columns:
        cand["Note_moyenne"] = pd.to_numeric(cand["Note_moyenne"], errors="coerce").fillna(0.0)
        cand = cand[cand["Note_moyenne"] >= float(min_rating)]

    cand = cand.sort_values("distance_cosine", ascending=True).head(int(top_n))

    preferred_cols = [
        "ID",
        "Titre",
        "Année_de_sortie",
        "Réalisateurs",
        "Note_moyenne",
        "Durée",
        "Genre",
        "Pays_origine",
        "distance_cosine",
    ]
    cols = [c for c in preferred_cols if c in cand.columns]
    other = [c for c in cand.columns if c not in cols]

    cand = cand[cols + other].drop(columns=["is_animation", "is_documentary", "is_horror"], errors="ignore")

    return cand.reset_index(drop=True)


def recommend(
    artifacts: dict,
    *,
    title_query: str,
    year: int | None = None,
    director_query: str | None = None,
    year_min: int = 1950,
    year_max: int = 2026,
    min_rating: float | None = None,
    top_n: int = 200,
    candidate_k: int = 1200,
    gated_lock: bool = True,
) -> pd.DataFrame:
    """
    Variante compatible "titre", mais sécurisée :
    - si titre ambigu (plusieurs lignes), exige year et/ou director_query,
      sinon lève une erreur explicite.
    - applique aussi le lock Animation/Documentary/Horror si gated_lock=True
    """
    df: pd.DataFrame = artifacts["df"]
    X = artifacts["X"]
    model: NearestNeighbors = artifacts["model"]

    if "Titre" not in df.columns:
        raise ValueError("Colonne 'Titre' introuvable dans la base.")

    t = str(title_query).strip().lower()
    base = df.copy()
    base["_t"] = base["Titre"].astype(str).str.strip().str.lower()
    matches = base[base["_t"].eq(t)].copy()

    if matches.empty:
        raise ValueError("Titre introuvable dans la base.")

    if year is not None and "Année_de_sortie" in matches.columns:
        y = int(year)
        matches["Année_de_sortie"] = pd.to_numeric(matches["Année_de_sortie"], errors="coerce").fillna(0).astype(int)
        matches = matches[matches["Année_de_sortie"].eq(y)]

    if director_query is not None:
        dq = clean_txt(director_query)
        if "txt_director" in matches.columns:
            matches = matches[matches["txt_director"].astype(str).str.contains(dq, na=False)]
        elif "Réalisateurs" in matches.columns:
            matches = matches[matches["Réalisateurs"].astype(str).map(clean_txt).str.contains(dq, na=False)]

    if matches.empty:
        opts_cols = [c for c in ["Titre", "Année_de_sortie", "Réalisateurs", "Note_moyenne"] if c in base.columns]
        opts = base[base["_t"].eq(t)][opts_cols].drop_duplicates().head(20)
        raise ValueError(
            "Titre ambigu, et aucun film ne correspond à tes filtres (année/réalisateur). "
            f"Options disponibles (extrait):\n{opts.to_string(index=False)}"
        )

    if len(matches) > 1:
        opts_cols = [c for c in ["Titre", "Année_de_sortie", "Réalisateurs", "Note_moyenne", "ID"] if c in matches.columns]
        opts = matches[opts_cols].drop_duplicates().head(20)
        raise ValueError(
            "Titre ambigu : plusieurs films correspondent. "
            "Passe year=... et/ou director_query=... (ou utilise recommend_by_id). "
            f"Options (extrait):\n{opts.to_string(index=False)}"
        )

    ref_idx = int(matches.index[0])
    ref_row = df.iloc[ref_idx]

    k = int(min(max(candidate_k, top_n + 50), X.shape[0]))
    distances, indices = model.kneighbors(X[ref_idx], n_neighbors=k)

    inds = indices.ravel().tolist()
    dists = distances.ravel().tolist()

    pairs = [(i, d) for i, d in zip(inds, dists) if i != ref_idx]

    cand = df.iloc[[i for i, _ in pairs]].copy()
    cand["distance_cosine"] = [d for _, d in pairs]


    if gated_lock:
        gated = artifacts.get("gated_genres", ("is_animation", "is_documentary", "is_horror"))
        cand = apply_gated_genre_lock(cand, ref_row=ref_row, gated=tuple(gated))

    if "Année_de_sortie" in cand.columns:
        cand["Année_de_sortie"] = pd.to_numeric(cand["Année_de_sortie"], errors="coerce").fillna(0).astype(int)
        cand = cand[(cand["Année_de_sortie"] >= int(year_min)) & (cand["Année_de_sortie"] <= int(year_max))]

    if min_rating is not None and "Note_moyenne" in cand.columns:
        cand["Note_moyenne"] = pd.to_numeric(cand["Note_moyenne"], errors="coerce").fillna(0.0)
        cand = cand[cand["Note_moyenne"] >= float(min_rating)]

    cand = cand.sort_values("distance_cosine", ascending=True).head(int(top_n))

    preferred_cols = [
        "Titre",
        "Année_de_sortie",
        "Réalisateurs",
        "Note_moyenne",
        "Durée",
        "Genre",
        "Pays_origine",
        "distance_cosine",
    ]
    cols = [c for c in preferred_cols if c in cand.columns]
    other = [c for c in cand.columns if c not in cols]
    cand = cand[cols + other].drop(columns=["is_animation", "is_documentary", "is_horror"], errors="ignore")

    return cand.reset_index(drop=True)
