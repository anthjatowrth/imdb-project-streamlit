from __future__ import annotations

from pathlib import Path
from typing import Final


# ---------- Lecture / ETL ----------
READ_OPTS: Final = {
    "sep": "\t",
    "compression": "gzip",
    "low_memory": False,
    "na_values": "\\N",
}
CHUNK: Final[int] = 500_000


# ---------- Sources ----------
BASICS_URL: Final[str] = "https://datasets.imdbws.com/title.basics.tsv.gz"
AKAS_URL: Final[str] = "https://datasets.imdbws.com/title.akas.tsv.gz"
RATINGS_URL: Final[str] = "https://datasets.imdbws.com/title.ratings.tsv.gz"
CREW_URL: Final[str] = "https://datasets.imdbws.com/title.crew.tsv.gz"
PRINCIPALS_URL: Final[str] = "https://datasets.imdbws.com/title.principals.tsv.gz"
NAMES_URL: Final[str] = "https://datasets.imdbws.com/name.basics.tsv.gz"


# ---------- Paths ----------
def find_project_root(start: Path) -> Path:
    """
    Remonte depuis 'start' jusqu'à trouver un dossier contenant 'data/'.
    Si non trouvé, fallback sur parent du fichier.
    """
    for p in [start, *start.parents]:
        if (p / "data").exists():
            return p
    return start.parent


ROOT: Final[Path] = find_project_root(Path(__file__).resolve())
DATA_DIR: Final[Path] = ROOT / "data"
RAW_DIR: Final[Path] = DATA_DIR / "raw"
INTERIM_DIR: Final[Path] = DATA_DIR / "interim"
OUTPUT_DIR: Final[Path] = DATA_DIR / "output"

TMDB_CSV_PATH: Final[Path] = RAW_DIR / "tmdb_full.csv"


def ensure_dirs() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    INTERIM_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)