# Global Seismic Trends

**Data-Driven Earthquake Analysis using Python, MySQL, SQL, and Streamlit**

---

## Overview

This project studies global earthquake activity through a complete data analytics workflow.  
Instead of treating earthquake records as isolated events, the project turns raw seismic data into a structured system for discovering trends, comparing regions, and understanding how earthquake magnitude, depth, timing, and tsunami risk behave over time.

The end result is not just a dataset. It is a full analytical pipeline with:

- automated data collection from the USGS Earthquake Catalog
- preprocessing and feature engineering in Python
- structured storage in MySQL
- analytical SQL queries for insight generation
- an interactive Streamlit dashboard for exploration

---

## Project Scope

The scope of this project is to build an end-to-end earthquake analytics solution that can:

- collect recent global earthquake events from a trusted public source
- clean and standardize messy raw seismic records
- enrich the dataset with business-friendly analytical fields
- support structured querying for trend and pattern discovery
- present findings through interactive visual analytics

This project focuses on earthquakes with magnitude `4.0+` collected across roughly the last 5 years of USGS records available in the pipeline.

---

## Why This Project Matters

Earthquakes are high-impact natural events that affect safety, infrastructure, emergency planning, and disaster response. Raw seismic feeds contain valuable information, but they are not immediately easy to analyze for patterns or decision-making.

This project is needed because it helps convert continuous earthquake event logs into a usable analytical system. With this workflow, we can:

- identify the most active seismic regions
- compare shallow, intermediate, and deep-focus earthquakes
- understand how magnitude relates to perceived significance
- examine tsunami-linked earthquake behavior
- study temporal patterns across years, months, weekdays, and hours
- evaluate reporting quality using station coverage and uncertainty metrics

---

## Problem Statement

Seismic data is publicly available, but it often arrives as large raw event records that are difficult to interpret directly. Analysts, students, and disaster-management teams need a cleaner way to move from raw data to meaningful insight.

This project addresses that gap by building a reproducible analytics workflow that transforms earthquake event data into a queryable and visual exploration platform.

---

## Data Snapshot

The cleaned project dataset currently contains:

- `75,853` earthquake records
- `34` columns after enrichment
- events spanning `2021` to `2026`
- coverage across `203` countries or location labels
- maximum recorded magnitude of `8.8`
- deepest recorded event at `681.24 km`

Core raw attributes include:

- event id and timestamps
- latitude, longitude, and depth
- magnitude and magnitude type
- place and reporting network
- tsunami flag and significance score
- uncertainty and station quality metrics

Derived analytical fields include:

- `country`
- `year`, `month`, `day`, `hour`
- `day_of_week`
- `depth_category`
- `severity`

---

## How The Project Is Done

### 1. Data Collection

The project fetches earthquake data from the **USGS Earthquake Catalog API**.  
Data is pulled month by month to cover multiple years while keeping API requests manageable and structured.

What happens in this stage:

- requests are sent to the USGS API in `geojson` format
- earthquake events with magnitude `>= 4.0` are collected
- useful fields are flattened from nested JSON into tabular records
- duplicate events are removed before saving

Output:

- `earthquake_raw.csv`

### 2. Data Cleaning and Enrichment

The raw file is transformed into an analysis-ready dataset using Pandas.

Cleaning work includes:

- converting epoch timestamps into UTC datetime values
- fixing numeric columns and handling missing values
- standardizing text fields
- dropping invalid rows missing critical seismic information
- extracting country names from location text

Feature engineering includes:

- time-based columns for trend analysis
- depth buckets: `Shallow`, `Intermediate`, `Deep`
- severity labels: `Minor`, `Moderate`, `Strong`, `Major`, `Great`

Output:

- `earthquake_clean.csv`

### 3. Database Modeling

The cleaned dataset is loaded into **MySQL** so that analytical queries can be executed efficiently.

This step enables:

- persistent structured storage
- SQL-based exploration
- grouped summaries and ranking queries
- trend comparisons using aggregations and window functions

Output:

- MySQL database: `seismic_db`
- table: `earthquakes`

### 4. Analysis Layer

The project includes **30 analytical SQL queries** grouped into major themes:

- magnitude and depth analysis
- time trend analysis
- significance and impact analysis
- event quality and reporting metrics
- tsunami-related patterns
- advanced spatial and temporal patterns

These queries help answer practical questions such as:

- Which countries are most seismically active?
- Which earthquakes were strongest or deepest?
- Which periods show the highest event frequency?
- How do tsunami earthquakes differ from non-tsunami earthquakes?
- Where is data quality weaker based on gap and RMS?

### 5. Visualization Layer

An interactive **Streamlit dashboard** turns the dataset into a visual exploration tool.

Dashboard outputs include:

- world epicenter map
- magnitude and depth distributions
- time-based trend charts
- tsunami-focused comparisons
- country-level activity rankings
- data quality analysis visuals
- raw filtered data explorer

---

## Project Workflow

```text
USGS API
   -> Raw Earthquake Records
   -> Python Data Cleaning
   -> Feature Engineering
   -> MySQL Storage
   -> SQL Analysis
   -> Streamlit Dashboard
   -> Visual Insights
```

---

## Key Outputs

This project produces four major outputs:

### 1. Raw Dataset

The original collected earthquake records saved from the API.

- `earthquake_raw.csv`

### 2. Clean Analytical Dataset

A structured and enriched version of the raw data ready for analysis.

- `earthquake_clean.csv`

### 3. SQL Insight Pack

A curated set of 30 SQL queries for answering analytical questions.

- `analytical_queries.sql`

### 4. Interactive Dashboard

A visual interface for exploring global seismic activity through filters and charts.

- `app.py`

---

## Analytical Areas Covered

### Magnitude and Depth

- strongest earthquakes
- deepest earthquakes
- shallow high-magnitude events
- average depth by country
- average magnitude by magnitude type

### Time Trends

- most active year
- most active month
- busiest day of the week
- hourly earthquake distribution
- year-over-year growth

### Tsunami and Impact Signals

- tsunami events by year
- significance comparisons
- severity distribution
- top countries for tsunami-linked earthquakes

### Quality and Reliability

- reviewed vs automatic events
- station coverage analysis
- RMS and gap quality patterns
- lower reliability event detection

### Regional Seismic Patterns

- top active countries
- shallow-to-deep ratios
- deep-focus hotspots
- activity score by country

---

## Technology Stack

| Layer | Tools Used |
|---|---|
| Data Source | USGS Earthquake Catalog API |
| Data Collection | Python, Requests |
| Data Processing | Pandas, NumPy, Regex |
| Storage | MySQL, SQLAlchemy, PyMySQL |
| Analysis | SQL |
| Visualization | Streamlit, Plotly |

---

## Project Structure

```text
EarthQuake_Analysis/
|-- fetch_earthquake_data.py
|-- preprocess.py
|-- load_to_mysql.py
|-- analytical_queries.sql
|-- app.py
|-- earthquake_raw.csv
|-- earthquake_clean.csv
|-- requirements.txt
|-- README.md
```

---

## What Makes This Project Strong

- It covers the full analytics lifecycle from ingestion to dashboarding.
- It converts raw geoscience data into decision-friendly analytical features.
- It combines Python, SQL, and BI-style visualization in one project.
- It is practical for portfolio use in data analytics, data engineering, and dashboard development.
- It demonstrates both technical execution and domain-focused insight generation.

---

## Possible Future Improvements

- add continent-level classification for stronger regional analysis
- integrate real-time refresh scheduling
- include alert-level or damage-related external datasets
- deploy the dashboard online for public access
- add forecasting or anomaly detection models
- support drill-downs for country and region detail pages

---

## Conclusion

Global Seismic Trends is an end-to-end earthquake analytics project built to transform raw seismic records into clear, structured, and interactive insight. It shows how public geospatial event data can be collected, cleaned, stored, queried, and visualized in a way that supports exploration, learning, and disaster-related analysis.

It is both a technical project and an analytical storytelling project, designed to make earthquake data easier to understand and more useful.
