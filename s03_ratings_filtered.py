import pandas as pd
from config import *
from utils import *

def run():
    df_movies = pd.read_parquet(INTERIM_DIR / "01_movies_ref.parquet")
    df_akas = pd.read_parquet(INTERIM_DIR / "02_akas_fr.parquet")

    # On ne garde que les films déjà validés par basics + titre FR
    tconst_set = set(df_movies.merge(df_akas, on="tconst", how="inner")["tconst"].tolist())

    df = pd.read_csv(RATINGS_URL, **READ_OPTS, usecols=["tconst","averageRating","numVotes"])
    df["tconst"] = clean_id_series(df["tconst"])
    df = df[df["tconst"].isin(tconst_set)].copy()

    df["averageRating"] = pd.to_numeric(df["averageRating"], errors="coerce")
    df["numVotes"] = to_int64_nullable(df["numVotes"])

    # ✅ Tes filtres le plus tôt possible
    df = df[df["averageRating"] >= 4].copy()
    df = df[((df["numVotes"] > 1000) & (df["averageRating"] > 7)) | (df["numVotes"] > 5000)].copy()

    out = INTERIM_DIR / "03_ratings_filtered.parquet"
    df.to_parquet(out, index=False)
    print(f"Saved: {out} ({len(df)} rows)")

    if __name__ == "__main__":
        run()