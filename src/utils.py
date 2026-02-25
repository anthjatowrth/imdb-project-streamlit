from __future__ import annotations

import re
import unicodedata
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from deep_translator import GoogleTranslator
from functools import lru_cache
import pycountry
from babel import Locale
import requests
import os

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

def resolve_poster_url(
    raw: Any,
    *,
    tmdb_base: str = "https://image.tmdb.org/t/p/w500",
    allow_local: bool = True,
) -> str | None:
    if raw is None:
        return None

    s = str(raw).strip()
    if not s or s.lower() == "nan":
        return None

    if s.startswith(("http://", "https://")):
        return s

    if s.startswith("//"):
        return "https:" + s

    if s.startswith("/"):
        return tmdb_base + s

    if allow_local and Path(s).exists():
        return s

    return None


def _fetch_omdb_poster(
    imdb_id: str,
    *,
    api_key: str,
    session: requests.Session | None = None,
    timeout: float = 8.0,
) -> str | None:
    if not api_key:
        return None

    sess = session or requests.Session()

    r = sess.get(
        "https://www.omdbapi.com/",
        params={"apikey": api_key, "i": imdb_id},
        timeout=timeout,
    )

    if r.status_code != 200:
        return None

    data = r.json()

    if data.get("Response") != "True":
        return None

    poster = data.get("Poster")

    if not poster or poster == "N/A":
        return None

    return poster


def pick_poster_url(
    row: pd.Series,
    cols: tuple[str, ...] = ("Poster1", "Poster2"),
    *,
    imdb_col: str = "ID",
    omdb_api_key: str | None = None,
    omdb_timeout: float = 8.0,
    session: requests.Session | None = None,
) -> str | None:
    """
    1) tente Poster1 / Poster2 (TMDB ou URL complète)
    2) si rien -> tente OMDb via IMDb ID
    """

    for c in cols:
        if c in row and pd.notna(row[c]):
            url = resolve_poster_url(row[c])
            if url:
                return url

    imdb_id = row.get(imdb_col)

    if not imdb_id:
        return None

    imdb_id = str(imdb_id).strip()

    if not imdb_id.startswith("tt"):
        return None

    key = omdb_api_key or os.getenv("OMDB_API_KEY")

    try:
        return _fetch_omdb_poster(
            imdb_id,
            api_key=key,
            session=session,
            timeout=omdb_timeout,
        )
    except Exception:
        return None


def parse_simple_list(s: Any) -> list[str]:
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



@lru_cache(maxsize=5000)
def translate_to_fr(text: str) -> str:
    if not text or not isinstance(text, str):
        return ""
    text = text.strip()
    if not text:
        return ""
    try:
        translated = GoogleTranslator(source="auto", target="fr").translate(text)
        return translated
    except Exception:
        return text
    

def format_votes(n: int | float | None, decimals: int = 1) -> str:
    if n is None:
        return "—"
    try:
        n = float(n)
    except (TypeError, ValueError):
        return "—"
    if n >= 1_000_000:
        value = n / 1_000_000
        return f"{value:.{decimals}f} M".replace(".", ",")
    elif n >= 1_000:
        value = n / 1_000
        return f"{value:.{decimals}f} k".replace(".", ",")
    else:
        return str(int(n))
    

def format_duration(minutes: int | float) -> str:
    hours = int(minutes) // 60
    mins = int(minutes) % 60

    if hours and mins:
        return f"{hours} h {mins} min"
    elif hours:
        return f"{hours} h"
    else:
        return f"{mins} min"


def format_countries_fr(codes: list[str] | None) -> str:
    if not codes:
        return "—"
    loc = Locale.parse("fr")
    names = []
    for code in codes:
        if not code:
            continue
        c = str(code).strip().upper()

        country = (
            pycountry.countries.get(alpha_2=c)
            or pycountry.countries.get(alpha_3=c))
        if country:
            name = loc.territories.get(country.alpha_2, country.name)
        else:
            name = c
        names.append(name)
    return ", ".join(names) if names else "—"