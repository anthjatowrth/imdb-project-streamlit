import pandas as pd
from config import *
from utils import *

def popularity_bucket(x):
    if pd.isna(x):
        return None
    x = float(x)
    if x >= 50000:
        return "Très populaire"
    elif 15000 < x < 50000:
        return "Populaire"
    elif 7500 < x <= 15000:
        return "Peu populaire"
    else:
        return "Faible notoriété"

def run():
    df_core = pd.read_parquet(INTERIM_DIR / "04_core_movies.parquet")
    df_crew = pd.read_parquet(INTERIM_DIR / "05_crew.parquet")
    df_cast = pd.read_parquet(INTERIM_DIR / "06_cast.parquet")
    df_prod = pd.read_parquet(INTERIM_DIR / "06_producers.parquet")
    df_names = pd.read_parquet(INTERIM_DIR / "07_names.parquet")

    name_map = dict(zip(df_names["nconst"].astype(str), df_names["primaryName"].astype(str)))

    # directors -> noms
    tmp = df_crew.copy()
    tmp["director_list"] = tmp["directors"].apply(split_csv_ids)
    df_directors = pd.DataFrame({
        "tconst": tmp["tconst"],
        "directors": tmp["director_list"].apply(lambda ns: join_names(ns, name_map))
    }).drop_duplicates("tconst")

    # cast -> noms
    df_cast2 = df_cast.copy()
    df_cast2["actors_top5"] = df_cast2["actors_top5_nconsts"].apply(lambda s: join_names(split_csv_ids(s), name_map))
    df_cast2 = df_cast2[["tconst","actors_top5"]]

    # producers -> noms
    df_prod2 = df_prod.copy()
    df_prod2["producers"] = df_prod2["producers_nconsts"].apply(lambda s: join_names(split_csv_ids(s), name_map))
    df_prod2 = df_prod2[["tconst","producers"]]

    df = (
        df_core
        .merge(df_directors, on="tconst", how="left")
        .merge(df_cast2, on="tconst", how="left")
        .merge(df_prod2, on="tconst", how="left")
    )

    # ici seulement : dropna directors/actors_top5 (car les noms existent maintenant)
    df = df.dropna(subset=["directors", "actors_top5"]).copy()

    # dédoublonnage logique
    df = df.sort_values("tconst").drop_duplicates(
        subset=["title_display_FR", "directors", "startYear"],
        keep="first"
    )

    # renommage FR (ta convention)
    df = df.rename(columns={
        "tconst":"ID",
        "title_display_FR":"Titre",
        "startYear":"Année_de_sortie",
        "runtimeMinutes":"Durée",
        "genres":"Genre",
        "averageRating":"Note_moyenne",
        "numVotes":"Nombre_votes",
        "directors":"Réalisateurs",
        "actors_top5":"Casting",
        "producers":"Producteurs",
    })

    df["Popularité"] = df["Nombre_votes"].astype(float).apply(popularity_bucket)

    out = OUTPUT_DIR / "08_imdb_clean.csv"
    df.to_csv(out, index=False, encoding="utf-8")
    print(f"Saved: {out} ({len(df)} rows)")

    if __name__ == "__main__":
        run()

