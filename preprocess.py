"""
Global Seismic Trends: Data-Driven Earthquake Insights
Step 2: Clean, transform, and enrich the raw earthquake dataset.
"""

import pandas as pd
import numpy as np
import re
import os

RAW_CSV    = "earthquake_raw.csv"
CLEAN_CSV  = "earthquake_clean.csv"


# ─────────────────────────────────────────────
# 1. Load
# ─────────────────────────────────────────────
def load_data(path: str = RAW_CSV) -> pd.DataFrame:
    df = pd.read_csv(path)
    print(f"Loaded {len(df)} rows, {df.shape[1]} columns.")
    return df


# ─────────────────────────────────────────────
# 2. Convert Timestamps
# ─────────────────────────────────────────────
def convert_timestamps(df: pd.DataFrame) -> pd.DataFrame:
    for col in ["time", "updated"]:
        # USGS returns milliseconds since epoch
        df[col] = pd.to_datetime(df[col], unit="ms", utc=True, errors="coerce")
    print("Timestamps converted.")
    return df


# ─────────────────────────────────────────────
# 3. Clean Numeric Fields
# ─────────────────────────────────────────────
NUMERIC_COLS = [
    "mag", "depth_km", "nst", "dmin", "rms", "gap",
    "magError", "depthError", "magNst", "sig", "tsunami",
    "latitude", "longitude"
]

def clean_numerics(df: pd.DataFrame) -> pd.DataFrame:
    for col in NUMERIC_COLS:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    # Fill missing values sensibly
    for col in ["nst", "dmin", "rms", "gap", "magError", "depthError", "magNst"]:
        df[col].fillna(df[col].median(), inplace=True)
    df["sig"].fillna(0, inplace=True)
    df["tsunami"].fillna(0, inplace=True)
    df.dropna(subset=["mag", "depth_km", "latitude", "longitude"], inplace=True)
    print(f"After numeric cleaning: {len(df)} rows remain.")
    return df


# ─────────────────────────────────────────────
# 4. Clean String / Text Fields
# ─────────────────────────────────────────────
STRING_COLS = ["magType", "status", "type", "net",
               "locationSource", "magSource", "types", "sources", "ids"]

def clean_strings(df: pd.DataFrame) -> pd.DataFrame:
    for col in STRING_COLS:
        df[col] = df[col].astype(str).str.strip().str.lower()
    df["place"] = df["place"].astype(str).str.strip()
    print("String fields cleaned.")
    return df


# ─────────────────────────────────────────────
# 5. Regex: Extract Country from Place
# ─────────────────────────────────────────────
COUNTRY_OVERRIDES = {
    "alaska":         "United States",
    "hawaii":         "United States",
    "puerto rico":    "United States",
    "california":     "United States",
    "nevada":         "United States",
    "oklahoma":       "United States",
    "washington":     "United States",
    "oregon":         "United States",
    "idaho":          "United States",
    "montana":        "United States",
    "wyoming":        "United States",
    "utah":           "United States",
    "colorado":       "United States",
    "b.c.":           "Canada",
    "british columbia": "Canada",
    "yukon":          "Canada",
}

def extract_country(place: str) -> str:
    """Extract country from USGS place string like '10km NE of City, Country'."""
    if not place or place == "nan":
        return "Unknown"
    # USGS format: "distance direction of City, Country"
    match = re.search(r',\s*(.+)$', place)
    if match:
        candidate = match.group(1).strip()
        # Check overrides
        for key, val in COUNTRY_OVERRIDES.items():
            if key in candidate.lower():
                return val
        return candidate
    # Fallback: check overrides on entire string
    lower_place = place.lower()
    for key, val in COUNTRY_OVERRIDES.items():
        if key in lower_place:
            return val
    return "Unknown"

def add_country(df: pd.DataFrame) -> pd.DataFrame:
    df["country"] = df["place"].apply(extract_country)
    print(f"Country extracted. Top 5: {df['country'].value_counts().head().to_dict()}")
    return df


# ─────────────────────────────────────────────
# 6. Derive Time Columns
# ─────────────────────────────────────────────
def add_time_columns(df: pd.DataFrame) -> pd.DataFrame:
    df["year"]        = df["time"].dt.year
    df["month"]       = df["time"].dt.month
    df["day"]         = df["time"].dt.day
    df["hour"]        = df["time"].dt.hour
    df["day_of_week"] = df["time"].dt.day_name()
    print("Time-derived columns added.")
    return df


# ─────────────────────────────────────────────
# 7. Depth Category
# ─────────────────────────────────────────────
def add_depth_category(df: pd.DataFrame) -> pd.DataFrame:
    def categorize(d):
        if d < 70:
            return "Shallow"
        elif d < 300:
            return "Intermediate"
        else:
            return "Deep"
    df["depth_category"] = df["depth_km"].apply(categorize)
    return df


# ─────────────────────────────────────────────
# 8. Magnitude / Severity Flag
# ─────────────────────────────────────────────
def add_severity_flag(df: pd.DataFrame) -> pd.DataFrame:
    def categorize(m):
        if m < 5.0:
            return "Minor"
        elif m < 6.0:
            return "Moderate"
        elif m < 7.0:
            return "Strong"
        elif m < 8.0:
            return "Major"
        else:
            return "Great"
    df["severity"] = df["mag"].apply(categorize)
    return df


# ─────────────────────────────────────────────
# Pipeline
# ─────────────────────────────────────────────
def preprocess(path: str = RAW_CSV, out: str = CLEAN_CSV) -> pd.DataFrame:
    df = load_data(path)
    df = convert_timestamps(df)
    df = clean_numerics(df)
    df = clean_strings(df)
    df = add_country(df)
    df = add_time_columns(df)
    df = add_depth_category(df)
    df = add_severity_flag(df)

    # Reset index
    df.reset_index(drop=True, inplace=True)
    df.to_csv(out, index=False)
    print(f"\nCleaned dataset saved → {out}  ({len(df)} rows, {df.shape[1]} cols)")
    return df


if __name__ == "__main__":
    preprocess()
