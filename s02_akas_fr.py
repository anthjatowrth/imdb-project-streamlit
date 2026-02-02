import pandas as pd
from config import *
from utils import *

def run():
    df_movies = pd.read_parquet(INTERIM_DIR / "01_movies_ref.parquet")
    tconst_set = set(df_movies["tconst"].dropna().tolist())

    rows = []
    usecols = ["titleId","title","types","region"]

    for chunk in pd.read_csv(AKAS_URL, **READ_OPTS, usecols=usecols, chunksize=CHUNK):
        chunk = chunk.rename(columns={"titleId":"tconst"})
        chunk["tconst"] = clean_id_series(chunk["tconst"])

        chunk = chunk[chunk["tconst"].isin(tconst_set)]
        if chunk.empty:
            continue

        chunk = chunk[chunk["region"] == "FR"]
        if chunk.empty:
            continue

        types_s = chunk["types"].astype("string").fillna("")
        chunk = chunk[types_s.str.contains(r"(?:^|,)imdbDisplay(?:,|$)", regex=True)]
        if chunk.empty:
            continue

        rows.append(chunk[["tconst","title","types"]])

    df = pd.concat(rows, ignore_index=True) if rows else pd.DataFrame(columns=["tconst","title","types"])
    if df.empty:
        out = INTERIM_DIR / "02_akas_fr.parquet"
        pd.DataFrame(columns=["tconst","title_display_FR"]).to_parquet(out, index=False)
        print(f"Saved: {out} (0 rows)")
        return

    df["types_clean"] = df["types"].astype("string").fillna("").str.strip()
    df["is_exact_imdbDisplay"] = (df["types_clean"] == "imdbDisplay").astype(int)

    df = (
        df.sort_values(["tconst","is_exact_imdbDisplay"], ascending=[True, False])
          .drop_duplicates("tconst", keep="first")
          .rename(columns={"title":"title_display_FR"})
          [["tconst","title_display_FR"]]
    )

    out = INTERIM_DIR / "02_akas_fr.parquet"
    df.to_parquet(out, index=False)
    print(f"Saved: {out} ({len(df)} rows)")

    if __name__ == "__main__":
        run()