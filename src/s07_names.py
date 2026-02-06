import pandas as pd
from config import *
from utils import *

def _read_ids(path):
    if not path.exists():
        return set()
    return set([line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()])

def run():
    directors = _read_ids(INTERIM_DIR / "05_director_nconsts.txt")
    principals = _read_ids(INTERIM_DIR / "06_principals_nconsts.txt")
    needed = directors.union(principals)

    rows = []
    for chunk in pd.read_csv(NAMES_URL, **READ_OPTS, usecols=["nconst","primaryName"], chunksize=CHUNK):
        chunk["nconst"] = clean_id_series(chunk["nconst"])
        chunk = chunk[chunk["nconst"].isin(needed)][["nconst","primaryName"]].copy()
        if not chunk.empty:
            rows.append(chunk)

    df = pd.concat(rows, ignore_index=True) if rows else pd.DataFrame(columns=["nconst","primaryName"])
    df = df.dropna(subset=["nconst","primaryName"]).drop_duplicates("nconst")
    df["primaryName"] = df["primaryName"].astype("string").str.strip()

    df.to_parquet(INTERIM_DIR / "07_names.parquet", index=False)
    print(f"Saved: {INTERIM_DIR/'07_names.parquet'} ({len(df)} rows)")

    if __name__ == "__main__":
        run()