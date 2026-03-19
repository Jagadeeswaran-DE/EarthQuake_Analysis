"""
Global Seismic Trends: Data-Driven Earthquake Insights
Step 1: Fetch earthquake data from the USGS API
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import os

# ─────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────
USGS_API_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"
OUTPUT_CSV   = "earthquake_raw.csv"
MIN_MAG      = 4.0          # minimum magnitude to keep (reduces noise)
YEARS_BACK   = 5            # how many years of history to pull


def date_range_months(years_back: int):
    """Generate (start, end) string pairs for each month going back `years_back` years."""
    today = datetime.utcnow()
    pairs = []
    for i in range(years_back * 12):
        end   = today.replace(day=1) - timedelta(days=1) * (i * 30)
        # safer: first day of the target month
        first = end.replace(day=1)
        last  = (first + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        pairs.append((first.strftime("%Y-%m-%d"), last.strftime("%Y-%m-%d")))
    return pairs


def fetch_month(start: str, end: str) -> list[dict]:
    """Fetch one month of earthquake data and return a list of flat dicts."""
    params = {
        "format":       "geojson",
        "starttime":    start,
        "endtime":      end,
        "minmagnitude": MIN_MAG,
        "limit":        20000,
        "orderby":      "time",
    }
    try:
        resp = requests.get(USGS_API_URL, params=params, timeout=60)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"  [WARN] Request failed for {start} → {end}: {e}")
        return []

    features = resp.json().get("features", [])
    records  = []
    for feat in features:
        props = feat.get("properties", {})
        geo   = feat.get("geometry", {}).get("coordinates", [None, None, None])

        records.append({
            "id":             feat.get("id"),
            "time":           props.get("time"),
            "updated":        props.get("updated"),
            "latitude":       geo[1],
            "longitude":      geo[0],
            "depth_km":       geo[2],
            "mag":            props.get("mag"),
            "magType":        props.get("magType"),
            "place":          props.get("place"),
            "status":         props.get("status"),
            "tsunami":        props.get("tsunami"),
            "sig":            props.get("sig"),
            "net":            props.get("net"),
            "nst":            props.get("nst"),
            "dmin":           props.get("dmin"),
            "rms":            props.get("rms"),
            "gap":            props.get("gap"),
            "magError":       props.get("magError"),
            "depthError":     props.get("depthError"),
            "magNst":         props.get("magNst"),
            "locationSource": props.get("locationSource"),
            "magSource":      props.get("magSource"),
            "types":          props.get("types"),
            "ids":            props.get("ids"),
            "sources":        props.get("sources"),
            "type":           props.get("type"),
        })
    return records


def fetch_all() -> pd.DataFrame:
    all_records = []
    months = date_range_months(YEARS_BACK)
    print(f"Fetching {len(months)} months of data (minMag={MIN_MAG}) …")

    for start, end in months:
        print(f"  {start} → {end}", end=" … ", flush=True)
        batch = fetch_month(start, end)
        print(f"{len(batch)} events")
        all_records.extend(batch)
        time.sleep(0.5)   # be polite to the API

    df = pd.DataFrame(all_records)
    df.drop_duplicates(subset="id", inplace=True)
    print(f"\nTotal unique events fetched: {len(df)}")
    return df


if __name__ == "__main__":
    df = fetch_all()
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"Raw data saved → {OUTPUT_CSV}")
