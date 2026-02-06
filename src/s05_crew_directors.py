import pandas as pd
from config import *
from utils import *

def run():
    df_core = pd.read_parquet(INTERIM_DIR / "04_core_movies.parquet")
    tconst_set = set(df_core["tconst"].tolist())

    rows = []
    director_nconsts = set()

    for chunk in pd.read_csv(CREW_URL, **READ_OPTS, usecols=["tconst","directors"], chunksize=CHUNK):
        chunk["tconst"] = clean_id_series(chunk["tconst"])
        chunk = chunk[chunk["tconst"].isin(tconst_set)].copy()
        if chunk.empty:
            continue

        # on retire directeurs manquants tout de suite (gain)
        dirs = chunk["directors"].astype("string").fillna("").str.strip()
        chunk = chunk[dirs.ne("") & dirs.ne("\\N")].copy()
        if chunk.empty:
            continue

        rows.append(chunk[["tconst","directors"]])
        for s in chunk["directors"]:
            director_nconsts.update(split_csv_ids(s))

    df_crew = pd.concat(rows, ignore_index=True) if rows else pd.DataFrame(columns=["tconst","directors"])

    df_crew.to_parquet(INTERIM_DIR / "05_crew.parquet", index=False)
    (INTERIM_DIR / "05_director_nconsts.txt").write_text("\n".join(sorted(director_nconsts)), encoding="utf-8")

    print(f"Saved: {INTERIM_DIR/'05_crew.parquet'} ({len(df_crew)} rows)")
    print(f"Saved: {INTERIM_DIR/'05_director_nconsts.txt'} ({len(director_nconsts)} ids)")

    if __name__ == "__main__":
        run()