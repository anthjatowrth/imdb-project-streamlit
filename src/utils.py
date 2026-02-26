from __future__ import annotations

import re
import unicodedata
import base64
import os
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import requests
import pycountry
import streamlit as st

from deep_translator import GoogleTranslator
from babel import Locale


# ── Données / pipeline ────────────────────────────────────────────────────────

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


def read_csv_clean_columns(path: str | Path, *, sep: str = ",") -> pd.DataFrame:
    df = pd.read_csv(path, sep=sep)
    df.columns = df.columns.str.strip()
    return df


# ── Texte / normalisation ─────────────────────────────────────────────────────

def clean_text(s: str) -> str:
    return " ".join(str(s).strip().split())


def normalize_txt(s: Any, *, collapse_spaces: bool = False) -> str:
    s = "" if s is None else str(s)
    s = s.strip().lower()
    s = "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))
    if collapse_spaces:
        s = re.sub(r"\s+", " ", s).strip()
    return s


def clean_txt_for_reco(s: Any) -> str:
    s = "" if s is None or (isinstance(s, float) and np.isnan(s)) else str(s)
    s = s.lower()
    s = re.sub(r"[,\|;/]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def parse_simple_list(s: Any) -> list[str]:
    if s is None or (isinstance(s, float) and np.isnan(s)):
        return []
    s = str(s).strip()
    if not s:
        return []
    s = s.replace("[", "").replace("]", "")
    parts = [p.strip().strip("'").strip('"') for p in s.split(",")]
    return [p for p in parts if p]


# ── Recherche par titre ───────────────────────────────────────────────────────

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


# ── Formatage ─────────────────────────────────────────────────────────────────

@st.cache_data(show_spinner=False, max_entries=10000)
def translate_to_fr(text: str) -> str:
    if not text or not isinstance(text, str):
        return ""
    text = text.strip()
    if not text:
        return ""
    try:
        return GoogleTranslator(source="auto", target="fr").translate(text)
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
        return f"{n / 1_000_000:.{decimals}f} M".replace(".", ",")
    elif n >= 1_000:
        return f"{n / 1_000:.{decimals}f} k".replace(".", ",")
    return str(int(n))


def format_duration(minutes: int | float) -> str:
    hours = int(minutes) // 60
    mins = int(minutes) % 60
    if hours and mins:
        return f"{hours} h {mins} min"
    elif hours:
        return f"{hours} h"
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
            or pycountry.countries.get(alpha_3=c)
        )
        name = loc.territories.get(country.alpha_2, country.name) if country else c
        names.append(name)
    return ", ".join(names) if names else "—"


# ── Posters ───────────────────────────────────────────────────────────────────

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


def _get_omdb_api_key(provided: str | None = None) -> str | None:
    """Récupère la clé OMDB depuis l'argument, st.secrets ou l'environnement."""
    if provided:
        return provided
    # Priorité : st.secrets (Streamlit Cloud / local secrets.toml)
    try:
        import streamlit as st
        key = st.secrets.get("OMDB_API_KEY")
        if key:
            return str(key)
    except Exception:
        pass
    # Fallback : variable d'environnement
    return os.getenv("OMDB_API_KEY") or None


def _fetch_omdb_poster(
    imdb_id: str,
    *,
    api_key: str,
    session: requests.Session | None = None,
    timeout: float = 8.0,
) -> str | None:
    if not api_key or not imdb_id:
        return None
    sess = session or requests.Session()
    try:
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
        poster = data.get("Poster", "")
        if not poster or poster == "N/A":
            return None
        return poster
    except Exception:
        return None


@st.cache_data(show_spinner=False, ttl=86400)  # cache 24h
def _cached_omdb_poster(imdb_id: str, api_key: str) -> str | None:
    """Cache les résultats OMDB pour éviter les appels réseau répétés."""
    return _fetch_omdb_poster(imdb_id, api_key=api_key)


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
    1) Tente Poster1 / Poster2 (TMDB ou URL complète).
    2) Si rien → tente OMDb via l'IMDb ID.
    """
    for c in cols:
        val = row[c] if c in row.index else None
        if val is not None and pd.notna(val):
            url = resolve_poster_url(val)
            if url:
                return url

    imdb_id = row[imdb_col] if imdb_col in row.index else None
    if not imdb_id:
        return None
    imdb_id = str(imdb_id).strip()
    if not imdb_id.startswith("tt"):
        return None

    key = _get_omdb_api_key(omdb_api_key)
    if not key:
        return None

    return _cached_omdb_poster(imdb_id, key)


# ── CSS / UI ──────────────────────────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def _build_css_payload(css_path: str, bg_path: str) -> str:
    """
    Construit le bloc <style> complet une seule fois, puis le met en cache
    pour toute la durée de vie du process (partagé entre tous les utilisateurs).
    Le fond PNG est redimensionné + converti en JPEG pour réduire drastiquement
    la taille du payload base64 (1.9 MB PNG → ~60-120 KB JPEG).
    """
    css = Path(css_path).read_text(encoding="utf-8")

    # Compression du fond : PNG 1.9 MB → JPEG ~80 KB
    try:
        from PIL import Image
        import io
        img = Image.open(bg_path).convert("RGB")
        # On descend à 1280px max (largeur d'affichage suffisante avec blur)
        img.thumbnail((1280, 1280), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=60, optimize=True)
        bg_bytes = buf.getvalue()
        mime = "image/jpeg"
    except Exception:
        # Fallback : PNG brut si Pillow absent
        bg_bytes = Path(bg_path).read_bytes()
        mime = "image/png"

    bg_b64 = base64.b64encode(bg_bytes).decode("utf-8")

    bg_css = f"""
    .stApp{{ position: relative; }}

    .stApp::before{{
        content:"";
        position: fixed;
        inset: -120px;
        background-image: url("data:{mime};base64,{bg_b64}");
        background-repeat: no-repeat;
        background-position: center;
        background-size: cover;
        opacity: 0.50;
        filter: blur(10px) saturate(1.05);
        transform: scale(1.08);
        pointer-events: none;
        z-index: 0;
    }}

    .stApp::after{{
        content:"";
        position: fixed;
        inset: 0;
        background:
            radial-gradient(circle at 20% 10%, rgba(123,104,238,0.10), transparent 55%),
            radial-gradient(circle at 85% 70%, rgba(123,104,238,0.30), transparent 55%),
            linear-gradient(180deg, rgba(15,14,26,0.50) 0%, rgba(15,14,26,0.55) 80%, rgba(15,14,26,1) 100%);
        pointer-events: none;
        z-index: 0;
    }}

    .stApp > *{{ position: relative; z-index: 1; }}
    """

    return f"<style>{css}\n{bg_css}</style>"


def load_css(
    css_path: str = "assets/style.css",
    bg_path: str = "assets/fond2.png",
) -> None:
    try:
        import streamlit as st
    except Exception:
        return

    payload = _build_css_payload(css_path, bg_path)
    st.markdown(payload, unsafe_allow_html=True)
