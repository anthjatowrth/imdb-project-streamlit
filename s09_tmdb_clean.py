import pandas as pd
from config import *
from utils import *

def run():
    df = pd.read_csv(TMDB_CSV_PATH, sep=",")

    df = df[df["adult"] == False].copy()
    df = df.drop(columns=["adult"], errors="ignore")
        
    df = df[df["video"] == False]
    df = df.drop(columns=["video"], errors="ignore")

    if "imdb_id" not in df.columns:
        raise ValueError("TMDB: colonne 'imdb_id' absente, impossible de merger sur IMDB.")

    df["imdb_id"] = clean_id_series(df["imdb_id"])
    df = df[df["imdb_id"].notna() & (df["imdb_id"].astype(str).str.len() > 2)].copy()

    df = df.drop(columns=[
        "budget","id","original_language","original_title","homepage","runtime","status","revenue","popularity",
        "production_companies_country","spoken_languages","vote_average","vote_count","release_date","title"
    ], errors="ignore")

    
    df["overview"] = df["overview"].str.replace("\n", " ", regex=False)
    df["overview"] = df["overview"].str.replace("\r", " ", regex=False)

    out = INTERIM_DIR / "09_tmdb_reduced.parquet"
    df.to_parquet(out, index=False)
    print(f"Saved: {out} ({len(df)} rows)")

    if __name__ == "__main__":
        run()