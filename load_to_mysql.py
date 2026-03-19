"""
Global Seismic Trends: Data-Driven Earthquake Insights
Step 3: Load cleaned DataFrame into MySQL using SQLAlchemy.

Prerequisites:
    pip install sqlalchemy pymysql
    MySQL server running with credentials below.
"""

import pandas as pd
from sqlalchemy import create_engine, text

# ─────────────────────────────────────────────
# Database Configuration  ← edit these
# ─────────────────────────────────────────────
DB_HOST   = "localhost"
DB_PORT   = 3306
DB_USER   = "root"
DB_PASS   = ""
DB_NAME   = "seismic_db"
TABLE     = "earthquakes"

CLEAN_CSV = "earthquake_clean.csv"


def get_engine():
    url = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(url, echo=False)
    return engine


CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS earthquakes (
    id               VARCHAR(50)  PRIMARY KEY,
    time             DATETIME,
    updated          DATETIME,
    latitude         DOUBLE,
    longitude        DOUBLE,
    depth_km         DOUBLE,
    mag              DOUBLE,
    magType          VARCHAR(20),
    place            TEXT,
    status           VARCHAR(30),
    tsunami          TINYINT,
    sig              INT,
    net              VARCHAR(20),
    nst              DOUBLE,
    dmin             DOUBLE,
    rms              DOUBLE,
    gap              DOUBLE,
    magError         DOUBLE,
    depthError       DOUBLE,
    magNst           DOUBLE,
    locationSource   VARCHAR(20),
    magSource        VARCHAR(20),
    types            TEXT,
    ids              TEXT,
    sources          TEXT,
    type             VARCHAR(30),
    -- Derived columns
    country          VARCHAR(100),
    year             SMALLINT,
    month            TINYINT,
    day              TINYINT,
    hour             TINYINT,
    day_of_week      VARCHAR(15),
    depth_category   VARCHAR(20),
    severity         VARCHAR(15)
);
"""


def create_database_if_needed(engine):
    with engine.connect() as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}`;"))
    print(f"Database `{DB_NAME}` ready.")


def load_to_mysql(csv_path: str = CLEAN_CSV):
    # Connect without specifying DB first to create it
    base_url = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/"
    base_engine = create_engine(base_url)
    create_database_if_needed(base_engine)

    engine = get_engine()
    with engine.connect() as conn:
        conn.execute(text(CREATE_TABLE_SQL))
        conn.commit()
    print(f"Table `{TABLE}` created / verified.")

    df = pd.read_csv(csv_path)
    # datetime columns
    for col in ["time", "updated"]:
        df[col] = pd.to_datetime(df[col], errors="coerce", utc=True).dt.tz_localize(None)

    # Insert in chunks (avoids memory issues for large datasets)
    df.to_sql(TABLE, con=engine, if_exists="replace",
              index=False, chunksize=1000, method="multi")
    print(f"Inserted {len(df)} rows into `{DB_NAME}`.`{TABLE}`.")


if __name__ == "__main__":
    load_to_mysql()
