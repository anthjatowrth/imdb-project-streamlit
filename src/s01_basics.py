import pandas as pd
from config import *
from utils import *

def run():
    usecols = ["tconst","titleType","isAdult","startYear","runtimeMinutes","genres"]
    df = pd.read_csv(BASICS_URL, **READ_OPTS, usecols=usecols)

    df["tconst"] = clean_id_series(df["tconst"])
    df["startYear"] = pd.to_numeric(df["startYear"], errors="coerce")
    df["runtimeMinutes"] = pd.to_numeric(df["runtimeMinutes"], errors="coerce")

    df = df[
        (df["titleType"] == "movie") &
        (df["isAdult"] == 0) &
        (df["startYear"] >= 1950) &
        (df["startYear"] < 2026)
    ].copy()

    # Documentary strict uniquement
    df = df[df["genres"].astype("string").fillna("").str.strip().ne("Documentary")].copy()

    # Horror strict uniquement (comme ton code)
    df = df[df["genres"].astype("string").fillna("").str.strip().ne("Horror")].copy()

    # Durée 50–200 min (tes filtres)
    df = df[(df["runtimeMinutes"] > 50) & (df["runtimeMinutes"] < 200)].copy()

    df = df[["tconst","startYear","runtimeMinutes","genres"]].copy()
    df["startYear"] = to_int64_nullable(df["startYear"])
    df["runtimeMinutes"] = to_int64_nullable(df["runtimeMinutes"])

    out = INTERIM_DIR / "01_movies_ref.parquet"
    df.to_parquet(out, index=False)
    print(f"Saved: {out} ({len(df)} rows)")

    if __name__ == "__main__":
        run()