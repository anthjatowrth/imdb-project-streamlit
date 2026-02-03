import pandas as pd
from config import *
from utils import *

def run():
    df_imdb = pd.read_csv(OUTPUT_DIR / "08_imdb_clean.csv")
    df_tmdb = pd.read_parquet(INTERIM_DIR / "09_tmdb_reduced.parquet").rename(columns={"imdb_id":"ID"})

    df_tmdb= df_tmdb.rename(columns={"backdrop_path":"Poster2","overview":"Résumé","poster_path":"Poster1",
                       "production_countries":"Pays_origine","tagline":"Accroche",
                       "production_companies_name":"Boite_de_production"})

    # évite collisions
    imdb_cols = set(df_imdb.columns)
    rename_tmdb = {c: f"TMDB_{c}" for c in df_tmdb.columns if c != "ID" and c in imdb_cols}
    if rename_tmdb:
        df_tmdb = df_tmdb.rename(columns=rename_tmdb)

    df_final = df_imdb.merge(df_tmdb, on="ID", how="left")

    out = OUTPUT_DIR / "10_final_imdb_tmdb.csv"
    df_final.to_csv(out, index=False, encoding="utf-8")
    print(f"Saved: {out} ({len(df_final)} rows)")

    if __name__ == "__main__":
        run()