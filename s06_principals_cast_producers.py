import pandas as pd
from collections import defaultdict
from config import *
from utils import *

def run():
    df_core = pd.read_parquet(INTERIM_DIR / "04_core_movies.parquet")
    tconst_set = set(df_core["tconst"].tolist())

    actors_candidates: dict[str, list[tuple[int, str]]] = defaultdict(list)
    producers_set: dict[str, set[str]] = defaultdict(set)
    needed_nconsts = set()

    usecols = ["tconst","nconst","category","ordering"]

    for chunk in pd.read_csv(PRINCIPALS_URL, **READ_OPTS, usecols=usecols, chunksize=CHUNK):
        chunk["tconst"] = clean_id_series(chunk["tconst"])
        chunk["nconst"] = clean_id_series(chunk["nconst"])

        chunk = chunk[
            chunk["tconst"].isin(tconst_set) &
            chunk["category"].isin(["actor","actress","producer"])
        ].copy()

        if chunk.empty:
            continue

        a = chunk[chunk["category"].isin(["actor","actress"])][["tconst","nconst","ordering"]].dropna()
        for t, n, o in a.itertuples(index=False):
            try:
                oi = int(o)
            except Exception:
                continue
            actors_candidates[t].append((oi, n))
            needed_nconsts.add(n)

        p = chunk[chunk["category"] == "producer"][["tconst","nconst"]].dropna()
        for t, n in p.itertuples(index=False):
            producers_set[t].add(n)
            needed_nconsts.add(n)

    rows_cast = []
    for t, lst in actors_candidates.items():
        lst.sort(key=lambda x: x[0])
        top, seen = [], set()
        for _, n in lst:
            if n not in seen:
                seen.add(n)
                top.append(n)
            if len(top) == 5:
                break
        rows_cast.append((t, ",".join(top)))

    df_cast = pd.DataFrame(rows_cast, columns=["tconst","actors_top5_nconsts"])
    df_prod = pd.DataFrame([(t, ",".join(sorted(ns))) for t, ns in producers_set.items()],
                           columns=["tconst","producers_nconsts"])

    df_cast.to_parquet(INTERIM_DIR / "06_cast.parquet", index=False)
    df_prod.to_parquet(INTERIM_DIR / "06_producers.parquet", index=False)
    (INTERIM_DIR / "06_principals_nconsts.txt").write_text("\n".join(sorted(needed_nconsts)), encoding="utf-8")

    print("Saved: 06_cast.parquet / 06_producers.parquet / 06_principals_nconsts.txt")

    if __name__ == "__main__":
        run()