from __future__ import annotations

import re
import unicodedata
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


def clean_id_series(s: pd.Series) -> pd.Series:
    return s.astype("string").str.strip()

def split_csv_ids(x) -> list[str]:
    if pd.isna(x):
        return []
    return [p.strip() for p in str(x).split(",") if p.strip()]

def join_unique_preserve_order(items: list[str]) -> list[str]:
    seen, out = set(), []
    for it in items:
        if it and it not in seen:
            seen.add(it)
            out.append(it)
    return out

def join_names(nconsts: list[str], name_map: dict[str, str]) -> str | None:
    if not nconsts:
        return None
    names = []
    for n in nconsts:
        nm = name_map.get(n)
        if isinstance(nm, str):
            nm = nm.strip()
            if nm:
                names.append(nm)
    names = join_unique_preserve_order(names)
    return ", ".join(names) if names else None

def to_int64_nullable(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce").astype("Int64")


def load_css(css_path: str = "assets/style.css") -> None:
    """
    Injecte un fichier CSS dans Streamlit.
    Import streamlit en local pour éviter de casser les scripts non-UI.
    """
    try:
        import streamlit as st
    except Exception:
        return

    p = Path(css_path)
    if p.exists():
        st.markdown(
            f"<style>{p.read_text(encoding='utf-8')}</style>",
            unsafe_allow_html=True,
        )
    p = Path(css_path)
    if p.exists():
        st.markdown(f"<style>{p.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


def clean_text(s: str) -> str:
    return " ".join(str(s).strip().split())


def normalize_txt(s: Any, *, collapse_spaces: bool = False) -> str:
    s = "" if s is None else str(s)
    s = s.strip().lower()
    s = "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))
    if collapse_spaces:
        s = re.sub(r"\s+", " ", s).strip()
    return s


def read_csv_clean_columns(path: str | Path, *, sep: str = ",") -> pd.DataFrame:
    df = pd.read_csv(path, sep=sep)
    df.columns = df.columns.str.strip()
    return df


def title_exists(df: pd.DataFrame, title: str, col: str = "Titre") -> bool:
    if not title:
        return False
    t = title.strip().lower()
    return bool(df[col].astype(str).str.strip().str.lower().eq(t).any())


def find_movie_row(df: pd.DataFrame, title: str, col: str = "Titre") -> pd.Series | None:
    if not title:
        return None
    t = title.strip().lower()
    mask = df[col].astype(str).str.strip().str.lower().eq(t)
    if not mask.any():
        return None
    return df.loc[mask].iloc[0]

def resolve_poster_url(raw: Any, *, tmdb_base: str = "https://image.tmdb.org/t/p/w500", allow_local: bool = True) -> str | None:
    if raw is None:
        return None
    s = str(raw).strip()
    if not s or s.lower() == "nan":
        return None

    if s.startswith("http://") or s.startswith("https://"):
        return s
    if s.startswith("//"):
        return "https:" + s
    if s.startswith("/"):
        return tmdb_base + s

    if allow_local and Path(s).exists():
        return s

    return None

def pick_poster_url(row: pd.Series, cols: tuple[str, ...] = ("Poster1", "Poster2")) -> str | None:
    for c in cols:
        if c in row and pd.notna(row[c]):
            url = resolve_poster_url(row[c])
            if url:
                return url
    return None


def parse_simple_list(s: Any) -> list[str]:
    """Parse une chaîne type "['France', 'USA']" ou "France, USA" en liste, robuste aux NaN."""
    if s is None or (isinstance(s, float) and np.isnan(s)):
        return []
    s = str(s).strip()
    if not s:
        return []
    s = s.replace("[", "").replace("]", "")
    parts = [p.strip().strip("'").strip('"') for p in s.split(",")]
    return [p for p in parts if p]


def clean_txt_for_reco(s: Any) -> str:
    s = "" if s is None or (isinstance(s, float) and np.isnan(s)) else str(s)
    s = s.lower()
    s = re.sub(r"[,\|;/]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s
