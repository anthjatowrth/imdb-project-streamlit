import os
import time
import importlib
from pathlib import Path

HERE = Path(__file__).resolve().parent

STEPS = [
    "s01_basics",
    "s02_akas_fr",
    "s03_ratings_filtered",
    "s04_core_movies",
    "s05_crew_directors",
    "s06_principals_cast_producers",
    "s07_names",
    "s08_imdb_final",
    "s09_tmdb_clean",
    "s10_merge_imdb_tmdb",
]

def main():
    os.chdir(HERE)

    print("PIPELINE FILE:", __file__)
    print("CWD:", os.getcwd())

    t0 = time.perf_counter()

    for name in STEPS:
        print(f"\n=== RUN {name}.py ===")
        start = time.perf_counter()

        try:
            mod = importlib.import_module(name)
            mod = importlib.reload(mod)  # utile quand tu modifies les scripts
        except Exception as e:
            print(f"❌ Import impossible pour {name}: {e}")
            raise

        if not hasattr(mod, "run"):
            raise AttributeError(f"❌ {name}.py n'a pas de fonction run()")

        mod.run()

        dt = time.perf_counter() - start
        print(f"✅ Done in {dt:.1f}s")

    total = time.perf_counter() - t0
    print(f"\n✅ Pipeline terminée en {total:.1f}s")

    # Check sortie attendue (adapte si ton nom de fichier est différent)
    out_csv = HERE.parent / "data" / "output" / "10_final_imdb_tmdb.csv"
    print("EXPECTED OUTPUT:", out_csv)
    print("EXISTS:", out_csv.exists())

if __name__ == "__main__":
    main()