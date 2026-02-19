import pandas as pd
from config import *
from utils import *
def run():
    df_movies = pd.read_parquet(INTERIM_DIR / "01_movies_ref.parquet")
    df_akas = pd.read_parquet(INTERIM_DIR / "02_akas_fr.parquet")
    df_r = pd.read_parquet(INTERIM_DIR / "03_ratings_filtered.parquet")

    df = (
        df_movies
        .merge(df_akas, on="tconst", how="inner")
        .merge(df_r, on="tconst", how="inner")  # inner = on garde ceux qui passent les filtres ratings
    )

    # ✅ Règle films > 2h (ici c’est le plus tôt possible)
    df = df[
        (df["runtimeMinutes"] <= 120) |
        (
            (df["runtimeMinutes"] >= 120) &
            (df["numVotes"] >= 25000) &
            (df["averageRating"] >= 7)
        )
    ].copy()

    out = INTERIM_DIR / "04_core_movies.parquet"
    df.to_parquet(out, index=False)
    print(f"Saved: {out} ({len(df)} rows)")

    if __name__ == "__main__":
        run()