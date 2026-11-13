"""
SWYNEX Task 1 - Data Cleaning & Preparation
Dataset: Netflix Movies and TV Shows (public, TidyTuesday 2021-04-20)
Usage:   python clean_data.py data/raw_data.csv data/cleaned_data.csv
"""
import sys
import numpy as np
import pandas as pd

log = []
def note(msg):
    print(msg); log.append(msg)

def profile(df, title):
    print(f"\n===== {title} =====")
    print("Shape:", df.shape)
    print("Missing cells:", int(df.isna().sum().sum()))
    print("Exact duplicates:", int(df.duplicated().sum()))
    print(df.dtypes.to_string())

def main(src, dst):
    df = pd.read_csv(src)
    raw_rows, raw_missing = len(df), int(df.isna().sum().sum())
    profile(df, "RAW")
    note(f"Raw dataset: {df.shape[0]} rows x {df.shape[1]} columns, {raw_missing} missing cells")

    # 1. Strip whitespace in every text column; blank strings -> NaN
    text_cols = df.select_dtypes(include=["object", "string"]).columns
    stripped = 0
    for c in text_cols:
        s = df[c].astype("string")
        stripped += int((s.notna() & (s != s.str.strip())).sum())
        df[c] = s.str.strip().replace("", pd.NA)
    note(f"Trimmed leading/trailing whitespace in {stripped} cells (e.g. date_added)")

    # 2. Duplicates: exact, and logical (same title + type + release_year, case-insensitive)
    exact = int(df.duplicated().sum())
    df = df.drop_duplicates()
    key = df[["title", "type", "release_year"]].assign(title=df["title"].str.lower())
    logical = int(key.duplicated().sum())
    df = df[~key.duplicated()].reset_index(drop=True)
    note(f"Removed {exact} exact and {logical} logical duplicate records")

    # 3. Data types
    df["date_added"] = pd.to_datetime(df["date_added"], format="%B %d, %Y", errors="coerce")
    note("Converted date_added from text ('August 14, 2020') to datetime")
    df["year_added"] = df["date_added"].dt.year.astype("Int64")
    df["month_added"] = df["date_added"].dt.month.astype("Int64")
    # duration mixes minutes (movies) and seasons (TV shows) -> split into number + unit
    dur = df["duration"].str.extract(r"(?P<n>\d+)\s*(?P<u>min|Season)", expand=True)
    df["duration_value"] = pd.to_numeric(dur["n"]).astype("Int64")
    df["duration_unit"] = dur["u"].map({"min": "minutes", "Season": "seasons"})
    df = df.drop(columns="duration")
    note("Split duration ('93 min' / '4 Seasons') into duration_value (int) and duration_unit")
    df["type"] = df["type"].astype("category")

    # 4. Inconsistent values
    before = df["rating"].nunique()
    df["rating"] = df["rating"].replace({"UR": "NR"})   # 'Unrated' and 'Not Rated' are the same
    note(f"Merged rating 'UR' into 'NR' (unrated == not rated): {before} -> {df['rating'].nunique()} categories")
    for c in ["country", "cast", "director", "listed_in"]:
        # normalise multi-value separators: single comma + space, drop empty items
        df[c] = df[c].apply(lambda v: pd.NA if pd.isna(v) else
                            ", ".join(p.strip() for p in str(v).split(",") if p.strip()) or pd.NA)
    note("Normalised comma-separated lists in country, cast, director, listed_in")
    df["primary_country"] = df["country"].str.split(",").str[0]
    df["primary_genre"] = df["listed_in"].str.split(",").str[0]
    note("Added primary_country and primary_genre helper columns for easy grouping")

    # 5. Missing values (fill categorical with 'Unknown' - never invent facts)
    for c in ["director", "cast", "country", "primary_country"]:
        n = int(df[c].isna().sum()); df[c] = df[c].fillna("Unknown")
        note(f"Filled {n} missing '{c}' with 'Unknown'")
    n = int(df["rating"].isna().sum()); df["rating"] = df["rating"].fillna("NR")
    note(f"Filled {n} missing 'rating' with 'NR'")
    n = int(df["date_added"].isna().sum())
    note(f"Left {n} missing date_added as NaT (cannot be inferred reliably)")

    # 6. Sanity checks
    bad = int((df["release_year"] > pd.Timestamp.today().year).sum())
    note(f"Validation: {bad} rows with release_year in the future; release_year range "
         f"{df['release_year'].min()}-{df['release_year'].max()}")
    assert df["show_id"].is_unique

    profile(df, "CLEANED")
    df.to_csv(dst, index=False)
    note(f"Saved {dst}: {df.shape[0]} rows x {df.shape[1]} columns, "
         f"{int(df.isna().sum().sum())} missing cells")
    with open("cleaning_log.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(log))

if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("Usage: python clean_data.py <raw.csv> <cleaned.csv>")
    main(*sys.argv[1:])
