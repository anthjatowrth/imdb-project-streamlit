import pandas as pd

def clean_id_series(s: pd.Series) -> pd.Series:
    return s.astype("string").str.strip()

def split_csv_ids(x) -> list[str]:
    if pd.isna(x):
        return []
    return [p.strip() for p in str(x).split(",") if p.strip()]

def join_unique_preserve_order(items: list[str]) -> list[str]:
    seen, out = set(), []
    for it in items:
        if it and it not in seen:
            seen.add(it)
            out.append(it)
    return out

def join_names(nconsts: list[str], name_map: dict[str, str]) -> str | None:
    if not nconsts:
        return None
    names = []
    for n in nconsts:
        nm = name_map.get(n)
        if isinstance(nm, str):
            nm = nm.strip()
            if nm:
                names.append(nm)
    names = join_unique_preserve_order(names)
    return ", ".join(names) if names else None

def to_int64_nullable(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce").astype("Int64")