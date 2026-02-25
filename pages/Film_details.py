from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from src.config import OUTPUT_DIR
from src.reco.engine import build_artifacts, recommend
from src.ui import render_sidebar
from src.utils import (
    load_css,
    pick_poster_url,
    read_csv_clean_columns,
    parse_simple_list,
    translate_to_fr,
    format_votes,
    format_duration,
    format_countries_fr,
)

st.set_page_config(page_title="Fiche film", layout="wide")
load_css()
render_sidebar()

st.markdown(
    """\
<style>
.left-wrap{max-width:410px;margin:0 auto;}
.poster-img{width:100%;max-height:800px;object-fit:cover;border-radius:16px;display:block;box-shadow:0 14px 35px rgba(0,0,0,.45);}

h1{font-size:46px !important;font-weight:800 !important;margin-bottom:.25rem !important;}
.blockquote-premium{font-size:20px;line-height:1.55;opacity:.95;padding:.75rem .9rem;border-left:4px solid rgba(126,229,167,.75);background:rgba(255,255,255,.03);border-radius:12px;}

[data-testid="stMarkdownContainer"] h2{font-size:28px !important;font-weight:750 !important;margin-top:1rem !important;}

.details-grid{display:grid;grid-template-columns:1fr 1fr;gap:.8rem 1.1rem;margin-top:.2rem;}
.detail-item{display:grid;grid-template-columns:22px 120px 1fr;align-items:start;gap:.55rem;padding:.55rem .65rem;border-radius:14px;border:1px solid rgba(255,255,255,.06);background:rgba(255,255,255,.02);}
.detail-ico{font-size:16px;opacity:.95;margin-top:1px;}
.detail-label{font-size:13px;opacity:.7;font-weight:650;letter-spacing:.2px;}
.detail-value{font-size:16px;opacity:.96;font-weight:520;line-height:1.45;}

.big-text{font-size:18px;line-height:1.75;opacity:.95;}
.text-box{border:1px solid rgba(255,255,255,.06);background:rgba(255,255,255,.02);border-radius:16px;padding:.9rem 1rem;}
.hr-soft{height:1px;background:rgba(255,255,255,.08);border:none;margin:1.1rem 0;}

.reco-grid { margin-top: 8px; margin-bottom: 10px; }

.mini-card{
  border: 1px solid rgba(255,255,255,0.08);
  background: rgba(255,255,255,0.03);
  border-radius: 16px;
  padding: 14px;
  box-shadow: 0 8px 16px rgba(0,0,0,0.25);
}

.mini-poster{
  width: 100%;
  height: 300px;
  object-fit: cover;
  border-radius: 10px;
  display: block;
  margin-bottom: 10px;
  background: rgba(255,255,255,0.04);
}

.mini-title{
  font-size: 0.98rem;
  line-height: 1.15;
  margin: 0 0 6px 0;
}

.mini-meta{
  font-size: 0.82rem;
  color: rgba(168,168,192,0.95);
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
""",
    unsafe_allow_html=True,
)

CSV_PATH = OUTPUT_DIR / "10_final_imdb_tmdb.csv"

@st.cache_data(show_spinner=False)
def load_df() -> pd.DataFrame:
    return read_csv_clean_columns(CSV_PATH)


@st.cache_resource(show_spinner=True)
def load_artifacts() -> dict:
    df_ = load_df()
    return build_artifacts(df_)


def _clip_text(s: Any, max_len: int = 34) -> str:
    txt = str(s) if s is not None else ""
    txt = txt.strip()
    if txt == "" or txt.lower() == "nan":
        return "—"
    if len(txt) <= max_len:
        return txt
    return txt[: max_len - 1].rstrip() + "…"


def _fmt_votes(v: Any) -> str:
    try:
        return f"{int(float(v)):,}".replace(",", " ")
    except Exception:
        return "—"


def _get_query_param(name: str) -> str:
    try:
        return str(st.query_params.get(name, "")).strip()
    except Exception:
        qp = st.experimental_get_query_params()
        v = qp.get(name, [""])
        return str(v[0] if isinstance(v, list) else v).strip()


df = load_df()

id_param = _get_query_param("id")
title_param = _get_query_param("title")

movie: pd.Series | None = None
if id_param:
    hit = df[df["ID"].astype(str) == str(id_param)]
    if not hit.empty:
        movie = hit.iloc[0]
else:
    hit = df[df["Titre"].astype(str) == str(title_param)]
    if not hit.empty:
        movie = hit.iloc[0]

if movie is None:
    st.error("Film introuvable (paramètre id/title).")
    st.stop()


poster_url_bg = pick_poster_url(movie)
if poster_url_bg:
    st.markdown(
        f"""
        <style>
        .bg-poster {{
            position: fixed;
            inset: 0;
            z-index: -2;
            background-image: url("{poster_url_bg}");
            background-size: cover;
            background-position: center;
            filter: blur(14px);
            transform: scale(1.12);
            opacity: 0.90;
        }}

        .bg-overlay {{
            position: fixed;
            inset: 0;
            z-index: -1;
            background:
              radial-gradient(ellipse at top, rgba(10,10,25,0.35) 0%, rgba(10,10,25,0.75) 70%),
              linear-gradient(to bottom, rgba(10,10,25,0.35), rgba(10,10,25,0.95));
        }}

        /* 🔥 Important : laisse voir le fond */
        .stApp {{
            background: transparent !important;
        }}
        </style>

        <div class="bg-poster"></div>
        <div class="bg-overlay"></div>
        """,
        unsafe_allow_html=True,
    )

country_clean = parse_simple_list(movie.get("Pays_origine", ""))
prod_clean = parse_simple_list(movie.get("Boite_de_production", ""))
country_text = format_countries_fr(country_clean)
prod_text = ", ".join(prod_clean)


left, right = st.columns([1.1, 2.2], vertical_alignment="top")

with left:
    st.markdown("""<div class="left-wrap">""", unsafe_allow_html=True)

    poster_url = pick_poster_url(movie)
    if poster_url:
        st.markdown(f"""<img class="poster-img" src="{poster_url}" />""", unsafe_allow_html=True)
    else:
        st.caption("Poster indisponible")

    year = movie.get("Année_de_sortie", None)
    rating = movie.get("Note_moyenne", None)
    votes = format_votes(movie.get("Nombre_votes", None))
    duration = format_duration(movie.get("Durée", None))

    m1, m2 = st.columns(2)
    with m1:
        st.metric("Année", int(year) if pd.notna(year) else "—")
        st.metric("Durée", duration)
    with m2:
        st.metric("Note", f"{float(rating):.1f}/10" if pd.notna(rating) else "—")
        st.metric("Votes", votes)

    st.divider()
    st.caption(f"Popularité : **{movie.get('Popularité', '—')}**")
    st.caption(f"Pays : **{country_text}**")

    st.markdown("""</div>""", unsafe_allow_html=True)

with right:
    title = movie.get("Titre", "—")
    st.markdown(f"# {title}")

    accroche = movie.get("Accroche", "")
    accroche_fr = f'"{translate_to_fr(accroche)}"' if accroche else ""
    if accroche_fr:
        st.markdown(f'<div class="blockquote-premium">{accroche_fr}</div>', unsafe_allow_html=True)

    st.markdown('<hr class="hr-soft"/>', unsafe_allow_html=True)

    st.subheader("Détails")

    v_genre = translate_to_fr(movie.get("Genre", "—")).replace(",",", ")
    v_dir = movie.get("Réalisateurs", "—")
    v_country = country_text or "—"
    v_pop = movie.get("Popularité", "—")

    v_prod = prod_text or "—"
    v_year = movie.get("Année_de_sortie", "—")
    v_dur = duration
    v_note = movie.get("Note_moyenne", "—")
    v_votes = format_votes(movie.get("Nombre_votes"))

    st.markdown(
        f"""\
<div class="details-grid">
  <div class="detail-item"><div class="detail-ico">🎭</div><div class="detail-label">Genre</div><div class="detail-value">{v_genre}</div></div>
  <div class="detail-item"><div class="detail-ico">🏢</div><div class="detail-label">Production</div><div class="detail-value">{v_prod}</div></div>

  <div class="detail-item"><div class="detail-ico">🎬</div><div class="detail-label">Réalisateurs</div><div class="detail-value">{v_dir}</div></div>
  <div class="detail-item"><div class="detail-ico">📅</div><div class="detail-label">Année</div><div class="detail-value">{v_year}</div></div>

  <div class="detail-item"><div class="detail-ico">🌍</div><div class="detail-label">Pays</div><div class="detail-value">{v_country}</div></div>
  <div class="detail-item"><div class="detail-ico">⏱️</div><div class="detail-label">Durée</div><div class="detail-value">{v_dur}</div></div>

  <div class="detail-item"><div class="detail-ico">🔥</div><div class="detail-label">Popularité</div><div class="detail-value">{v_pop}</div></div>
  <div class="detail-item"><div class="detail-ico">⭐</div><div class="detail-label">Note / Votes</div><div class="detail-value">{v_note}&nbsp;&nbsp;·&nbsp;&nbsp;{v_votes}</div></div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown('<hr class="hr-soft"/>', unsafe_allow_html=True)

    st.subheader("📖 Résumé")
    resume_fr = translate_to_fr(movie.get("Résumé", "") or "")
    if resume_fr:
        st.markdown(f'<div class="text-box big-text">{resume_fr}</div>', unsafe_allow_html=True)
    else:
        st.caption("Aucun résumé.")

    st.markdown('<hr class="hr-soft"/>', unsafe_allow_html=True)

    st.subheader("🧑‍🤝‍🧑 Casting")
    casting = str(movie.get("Casting", "") or "").strip()
    if casting:
        st.markdown(f'<div class="text-box big-text">{casting}</div>', unsafe_allow_html=True)
    else:
        st.caption("Casting indisponible.")

# ----------------------------
# ✅ Recos en pleine largeur (hors colonnes)
# ----------------------------
st.markdown('<hr class="hr-soft"/>', unsafe_allow_html=True)
st.markdown(
    """
    <h2 class="reco-title-section">Vous aimerez aussi...</h2>
    """,
    unsafe_allow_html=True,
)

artifacts = load_artifacts()

try:
    recs = recommend(
        artifacts,
        movie_id=movie.get("ID"),
        top_n=5,
        candidate_k=1200,
        gated_lock=False,  # "sans conditions"
        year_min=0,
        year_max=9999,
        min_rating=None,
    )
except Exception:
    recs = pd.DataFrame()

if recs is None or recs.empty:
    st.caption("Aucune recommandation disponible.")
else:
    cols = st.columns(5, gap="medium", vertical_alignment="top")

    for i, (_, row) in enumerate(recs.head(5).iterrows()):
        with cols[i]:
            poster_url = pick_poster_url(row)

            full_title = str(row.get("Titre", "—"))
            title_short = _clip_text(full_title, max_len=34)

            year = row.get("Année_de_sortie", "—")
            rating = row.get("Note_moyenne", "—")
            votes = row.get("Nombre_votes", "—")

            genre = row.get("Genre", "—")
            director = row.get("Réalisateurs", "—")

            if poster_url:
                poster_html = f"<img class='mini-poster' src='{poster_url}' alt='poster'/>"
            else:
                poster_html = (
                    "<div class='mini-poster' "
                    "style='display:flex;align-items:center;justify-content:center;'>"
                    "<span style='font-size:0.8rem;color:rgba(168,168,192,0.95)'>Poster indisponible</span>"
                    "</div>"
                )

            st.markdown(
                f"""
                <div class="mini-card" title="{full_title} • {year} • {director} • {genre}">
                  {poster_html}
                  <div class="mini-title"><b>{title_short}</b></div>
                  <p class="mini-meta">{year} • ⭐ {rating} • 👥 {_fmt_votes(votes)}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.page_link(
                "pages/Film_details.py",
                label="Voir la fiche",
                query_params={"id": str(row["ID"])},
            )

    st.markdown("<div class='reco-grid'></div>", unsafe_allow_html=True)