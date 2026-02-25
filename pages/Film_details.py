from __future__ import annotations

import pandas as pd
import streamlit as st

from src.config import OUTPUT_DIR
from src.ui import render_sidebar
from src.utils import (
    load_css,
    pick_poster_url,
    read_csv_clean_columns,
    parse_simple_list,
    translate_to_fr,
    format_votes,
)

st.set_page_config(page_title="Fiche film", layout="wide")
load_css()
render_sidebar()

st.markdown("""\
<style>
.left-wrap{max-width:410px;margin:0 auto;}
.poster-img{width:100%;max-height:610px;object-fit:cover;border-radius:16px;display:block;box-shadow:0 14px 35px rgba(0,0,0,.45);}

h1{font-size:46px !important;font-weight:800 !important;margin-bottom:.25rem !important;}
.blockquote-premium{font-size:20px;line-height:1.55;opacity:.95;padding:.75rem .9rem;border-left:4px solid rgba(126,229,167,.75);background:rgba(255,255,255,.03);border-radius:12px;}

[data-testid="stMarkdownContainer"] h2{font-size:28px !important;font-weight:750 !important;margin-top:1rem !important;}

.chips{display:flex;flex-wrap:wrap;gap:.45rem;margin:.35rem 0 .9rem 0;}
.chip{font-size:14px;padding:6px 10px;border-radius:999px;border:1px solid rgba(255,255,255,.08);background:rgba(255,255,255,.03);opacity:.95;}

.details-grid{display:grid;grid-template-columns:1fr 1fr;gap:.8rem 1.1rem;margin-top:.2rem;}
.detail-item{display:grid;grid-template-columns:22px 120px 1fr;align-items:start;gap:.55rem;padding:.55rem .65rem;border-radius:14px;border:1px solid rgba(255,255,255,.06);background:rgba(255,255,255,.02);}
.detail-ico{font-size:16px;opacity:.95;margin-top:1px;}
.detail-label{font-size:13px;opacity:.7;font-weight:650;letter-spacing:.2px;}
.detail-value{font-size:16px;opacity:.96;font-weight:520;line-height:1.45;}

.big-text{font-size:18px;line-height:1.75;opacity:.95;}
.text-box{border:1px solid rgba(255,255,255,.06);background:rgba(255,255,255,.02);border-radius:16px;padding:.9rem 1rem;}
.hr-soft{height:1px;background:rgba(255,255,255,.08);border:none;margin:1.1rem 0;}
</style>
""", unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def load_df() -> pd.DataFrame:
    return read_csv_clean_columns(OUTPUT_DIR / "10_final_imdb_tmdb.csv")


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

if id_param:
    movie = df[df["ID"].astype(str) == str(id_param)].iloc[0]
else:
    movie = df[df["Titre"].astype(str) == str(title_param)].iloc[0]

left, right = st.columns([1.1, 2.2], vertical_alignment="top")

country_clean = parse_simple_list(movie.get("Pays_origine", ""))
prod_clean = parse_simple_list(movie.get("Boite_de_production", ""))

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
    duration = movie.get("Durée", None)

    m1, m2 = st.columns(2)
    with m1:
        st.metric("Année", int(year) if pd.notna(year) else "—")
        st.metric("Durée", f"{int(duration)} min" if pd.notna(duration) else "—")
    with m2:
        st.metric("Note", f"{float(rating):.1f}/10" if pd.notna(rating) else "—")
        st.metric("Votes", votes)

    st.divider()
    st.caption(f"Popularité : **{movie.get('Popularité', '—')}**")
    st.caption(f"Pays : **{country_clean}**")

    st.markdown("""</div>""", unsafe_allow_html=True)

with right:
    title = movie.get("Titre", "—")
    st.markdown(f"# {title}")

    genre = str(movie.get("Genre", "")).strip()
    directors = str(movie.get("Réalisateurs", "")).strip()

    accroche = movie.get("Accroche", "")
    accroche_fr = translate_to_fr(accroche)

    chips = []
    if genre:
        chips.append(f'<span class="chip">🎭 {genre}</span>')
    if directors:
        chips.append(f'<span class="chip">🎬 {directors}</span>')
    if prod_clean:
        chips.append(f'<span class="chip">🏢 {prod_clean}</span>')

    if chips:
        st.markdown(f'<div class="chips">{"".join(chips)}</div>', unsafe_allow_html=True)

    if accroche_fr:
        st.markdown(f'<div class="blockquote-premium">{accroche_fr}</div>', unsafe_allow_html=True)

    st.markdown('<hr class="hr-soft"/>', unsafe_allow_html=True)

    st.subheader("Détails")

    v_genre = movie.get("Genre", "—")
    v_dir = movie.get("Réalisateurs", "—")
    v_country = country_clean or "—"
    v_pop = movie.get("Popularité", "—")

    v_prod = prod_clean or "—"
    v_year = movie.get("Année_de_sortie", "—")
    v_dur = movie.get("Durée", "—")
    v_note = movie.get("Note_moyenne", "—")
    v_votes = format_votes(movie.get("Nombre_votes"))

    st.markdown(f"""\
<div class="details-grid">
  <div class="detail-item"><div class="detail-ico">🎭</div><div class="detail-label">Genre</div><div class="detail-value">{v_genre}</div></div>
  <div class="detail-item"><div class="detail-ico">🏢</div><div class="detail-label">Production</div><div class="detail-value">{v_prod}</div></div>

  <div class="detail-item"><div class="detail-ico">🎬</div><div class="detail-label">Réalisateurs</div><div class="detail-value">{v_dir}</div></div>
  <div class="detail-item"><div class="detail-ico">📅</div><div class="detail-label">Année</div><div class="detail-value">{v_year}</div></div>

  <div class="detail-item"><div class="detail-ico">🌍</div><div class="detail-label">Pays</div><div class="detail-value">{v_country}</div></div>
  <div class="detail-item"><div class="detail-ico">⏱️</div><div class="detail-label">Durée</div><div class="detail-value">{v_dur} min</div></div>

  <div class="detail-item"><div class="detail-ico">🔥</div><div class="detail-label">Popularité</div><div class="detail-value">{v_pop}</div></div>
  <div class="detail-item"><div class="detail-ico">⭐</div><div class="detail-label">Note / Votes</div><div class="detail-value">{v_note} · {v_votes}</div></div>
</div>
""", unsafe_allow_html=True)

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