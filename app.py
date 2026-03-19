import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import re
from datetime import datetime

# ─────────────────────────────────────────────
# Page Config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Global Seismic Trends",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# Custom CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.main {background: #0a0e1a;}

/* Header */
.hero-title {
    font-family: 'Space Mono', monospace;
    font-size: 2.6rem;
    font-weight: 700;
    color: #ff6b35;
    letter-spacing: -1px;
    line-height: 1.1;
}
.hero-sub {
    font-family: 'DM Sans', sans-serif;
    font-size: 1.05rem;
    color: #8899bb;
    margin-top: 0.3rem;
}

/* KPI cards */
.kpi-card {
    background: linear-gradient(135deg, #12172b 0%, #1a2040 100%);
    border: 1px solid #2a3560;
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    text-align: center;
}
.kpi-value {
    font-family: 'Space Mono', monospace;
    font-size: 2rem;
    font-weight: 700;
    color: #ff6b35;
}
.kpi-label {
    font-size: 0.78rem;
    color: #6677aa;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 0.2rem;
}

/* Section headers */
.section-header {
    font-family: 'Space Mono', monospace;
    font-size: 1.1rem;
    color: #ff6b35;
    border-left: 3px solid #ff6b35;
    padding-left: 0.6rem;
    margin: 1.5rem 0 0.8rem 0;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #080c18 !important;
    border-right: 1px solid #1e2640;
}

/* Tabs */
.stTabs [data-baseweb="tab"] {
    font-family: 'Space Mono', monospace;
    font-size: 0.82rem;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Data Loading
# ─────────────────────────────────────────────
USE_MYSQL = False   # ← set True to use MySQL

DB_HOST = "localhost"
DB_PORT = 3306
DB_USER = "root"
DB_PASS = "your_password"
DB_NAME = "seismic_db"
TABLE   = "earthquakes"


@st.cache_data(show_spinner="Loading seismic data …")
def load_data() -> pd.DataFrame:
    if USE_MYSQL:
        from sqlalchemy import create_engine
        engine = create_engine(
            f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        )
        df = pd.read_sql(f"SELECT * FROM {TABLE}", con=engine)
    else:
        df = pd.read_csv("earthquake_clean.csv")

    # Ensure datetime
    for col in ["time", "updated"]:
        df[col] = pd.to_datetime(df[col], errors="coerce", utc=True)

    # Numeric guard
    for col in ["mag", "depth_km", "latitude", "longitude", "sig", "nst",
                "dmin", "rms", "gap", "magError", "depthError", "tsunami"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df.dropna(subset=["mag", "latitude", "longitude"], inplace=True)
    return df


df_full = load_data()


# ─────────────────────────────────────────────
# Sidebar Filters
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🌍 **Seismic Explorer**")
    st.markdown("---")

    years = sorted(df_full["year"].dropna().unique().astype(int).tolist())
    selected_years = st.select_slider(
        "Year Range",
        options=years,
        value=(min(years), max(years)),
    )

    mag_range = st.slider(
        "Magnitude Range",
        float(df_full["mag"].min()),
        float(df_full["mag"].max()),
        (4.0, float(df_full["mag"].max())),
        step=0.1,
    )

    depth_cats = st.multiselect(
        "Depth Category",
        options=["Shallow", "Intermediate", "Deep"],
        default=["Shallow", "Intermediate", "Deep"],
    )

    top_countries = (
        df_full["country"].value_counts().head(30).index.tolist()
        + ["Unknown"]
    )
    all_countries = sorted(df_full["country"].unique().tolist())
    selected_countries = st.multiselect(
        "Filter Countries (optional)",
        options=all_countries,
        default=[],
        placeholder="All countries",
    )

    tsunami_filter = st.checkbox("Tsunami events only", value=False)

    st.markdown("---")
    st.caption("Data: USGS Earthquake Catalog")
    st.caption(f"Last refreshed: {datetime.now().strftime('%Y-%m-%d')}")


# ─────────────────────────────────────────────
# Apply Filters
# ─────────────────────────────────────────────
df = df_full.copy()
df = df[df["year"].between(selected_years[0], selected_years[1])]
df = df[df["mag"].between(mag_range[0], mag_range[1])]
df = df[df["depth_category"].isin(depth_cats)]
if selected_countries:
    df = df[df["country"].isin(selected_countries)]
if tsunami_filter:
    df = df[df["tsunami"] == 1]


# ─────────────────────────────────────────────
# Hero Header
# ─────────────────────────────────────────────
st.markdown("""
<div style='padding: 1.5rem 0 1rem 0;'>
  <div class='hero-title'>🌐 Global Seismic Trends</div>
  <div class='hero-sub'>Data-Driven Earthquake Insights &nbsp;·&nbsp; USGS Catalog</div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# KPI Row
# ─────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)

with k1:
    st.markdown(f"""
    <div class='kpi-card'>
        <div class='kpi-value'>{len(df):,}</div>
        <div class='kpi-label'>Total Events</div>
    </div>""", unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class='kpi-card'>
        <div class='kpi-value'>{df['mag'].max():.1f}</div>
        <div class='kpi-label'>Max Magnitude</div>
    </div>""", unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class='kpi-card'>
        <div class='kpi-value'>{df['depth_km'].max():.0f} km</div>
        <div class='kpi-label'>Deepest Quake</div>
    </div>""", unsafe_allow_html=True)

with k4:
    tsunami_count = int(df["tsunami"].sum())
    st.markdown(f"""
    <div class='kpi-card'>
        <div class='kpi-value'>{tsunami_count:,}</div>
        <div class='kpi-label'>Tsunami Events</div>
    </div>""", unsafe_allow_html=True)

with k5:
    st.markdown(f"""
    <div class='kpi-card'>
        <div class='kpi-value'>{df['country'].nunique()}</div>
        <div class='kpi-label'>Countries</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Tabs
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🗺️ World Map",
    "📊 Magnitude & Depth",
    "🕐 Time Trends",
    "🌊 Tsunamis & Alerts",
    "🔬 Advanced Analytics",
])


# ════════════════════════════════════════════
# TAB 1 – WORLD MAP
# ════════════════════════════════════════════
with tab1:
    st.markdown("<div class='section-header'>Earthquake Epicenter Map</div>",
                unsafe_allow_html=True)

    color_by = st.radio(
        "Color by",
        ["Magnitude", "Depth (km)", "Severity"],
        horizontal=True,
    )

    map_df = df.dropna(subset=["latitude", "longitude"])

    if color_by == "Magnitude":
        fig_map = px.scatter_mapbox(
            map_df, lat="latitude", lon="longitude",
            color="mag", size=map_df["mag"].clip(4, 9),
            color_continuous_scale="Inferno",
            size_max=15, zoom=1,
            hover_data={"place": True, "mag": True, "depth_km": True, "time": True},
            labels={"mag": "Magnitude"},
        )
    elif color_by == "Depth (km)":
        fig_map = px.scatter_mapbox(
            map_df, lat="latitude", lon="longitude",
            color="depth_km", size=map_df["mag"].clip(4, 9),
            color_continuous_scale="Viridis",
            size_max=15, zoom=1,
            hover_data={"place": True, "mag": True, "depth_km": True},
            labels={"depth_km": "Depth (km)"},
        )
    else:
        severity_order = ["Minor", "Moderate", "Strong", "Major", "Great"]
        severity_colors = {
            "Minor": "#4fc3f7", "Moderate": "#fff176",
            "Strong": "#ffb74d", "Major": "#ef5350", "Great": "#b71c1c"
        }
        map_df["sev_color"] = map_df["severity"].map(severity_colors)
        fig_map = px.scatter_mapbox(
            map_df, lat="latitude", lon="longitude",
            color="severity", size=map_df["mag"].clip(4, 9),
            color_discrete_map=severity_colors,
            category_orders={"severity": severity_order},
            size_max=18, zoom=1,
            hover_data={"place": True, "mag": True, "depth_km": True},
        )

    fig_map.update_layout(
        mapbox_style="carto-darkmatter",
        paper_bgcolor="#0a0e1a",
        plot_bgcolor="#0a0e1a",
        margin=dict(l=0, r=0, t=0, b=0),
        height=580,
        coloraxis_colorbar=dict(title_font_color="#aabbdd", tickfont_color="#aabbdd"),
        legend_font_color="#aabbdd",
    )
    st.plotly_chart(fig_map, use_container_width=True)

    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown("<div class='section-header'>Top 10 Strongest Events</div>",
                    unsafe_allow_html=True)
        top10 = (df.nlargest(10, "mag")
                   [["place", "country", "mag", "depth_km", "time"]]
                   .reset_index(drop=True))
        top10.index += 1
        top10["time"] = top10["time"].dt.strftime("%Y-%m-%d %H:%M")
        st.dataframe(top10, use_container_width=True)

    with col_r:
        st.markdown("<div class='section-header'>Top 10 Deepest Events</div>",
                    unsafe_allow_html=True)
        top10d = (df.nlargest(10, "depth_km")
                    [["place", "country", "mag", "depth_km", "time"]]
                    .reset_index(drop=True))
        top10d.index += 1
        top10d["time"] = top10d["time"].dt.strftime("%Y-%m-%d %H:%M")
        st.dataframe(top10d, use_container_width=True)


# ════════════════════════════════════════════
# TAB 2 – MAGNITUDE & DEPTH
# ════════════════════════════════════════════
with tab2:
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("<div class='section-header'>Magnitude Distribution</div>",
                    unsafe_allow_html=True)
        fig_hist = px.histogram(
            df, x="mag", nbins=60,
            color_discrete_sequence=["#ff6b35"],
            labels={"mag": "Magnitude", "count": "Count"},
        )
        fig_hist.update_layout(
            paper_bgcolor="#12172b", plot_bgcolor="#12172b",
            font_color="#aabbdd", bargap=0.05,
            xaxis=dict(gridcolor="#1e2640"),
            yaxis=dict(gridcolor="#1e2640"),
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    with c2:
        st.markdown("<div class='section-header'>Depth Distribution by Category</div>",
                    unsafe_allow_html=True)
        fig_dep = px.histogram(
            df, x="depth_km", color="depth_category",
            nbins=60,
            color_discrete_map={
                "Shallow": "#4fc3f7",
                "Intermediate": "#ff9800",
                "Deep": "#b71c1c",
            },
            labels={"depth_km": "Depth (km)"},
        )
        fig_dep.update_layout(
            paper_bgcolor="#12172b", plot_bgcolor="#12172b",
            font_color="#aabbdd", bargap=0.05,
            xaxis=dict(gridcolor="#1e2640"),
            yaxis=dict(gridcolor="#1e2640"),
        )
        st.plotly_chart(fig_dep, use_container_width=True)

    st.markdown("<div class='section-header'>Magnitude vs Depth Scatter</div>",
                unsafe_allow_html=True)
    sample = df.sample(min(5000, len(df)), random_state=42)
    fig_scat = px.scatter(
        sample, x="depth_km", y="mag",
        color="severity",
        color_discrete_map={
            "Minor": "#4fc3f7", "Moderate": "#fff176",
            "Strong": "#ffb74d", "Major": "#ef5350", "Great": "#b71c1c"
        },
        opacity=0.6,
        labels={"depth_km": "Depth (km)", "mag": "Magnitude"},
        hover_data=["place", "country"],
        size_max=6,
    )
    fig_scat.update_layout(
        paper_bgcolor="#12172b", plot_bgcolor="#12172b",
        font_color="#aabbdd",
        xaxis=dict(gridcolor="#1e2640"),
        yaxis=dict(gridcolor="#1e2640"),
        height=420,
    )
    st.plotly_chart(fig_scat, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        st.markdown("<div class='section-header'>Avg Magnitude by Type</div>",
                    unsafe_allow_html=True)
        mag_type = (df.groupby("magType")["mag"]
                      .agg(["mean", "count"])
                      .rename(columns={"mean": "avg_mag", "count": "events"})
                      .reset_index()
                      .query("events >= 10")
                      .sort_values("avg_mag", ascending=False))
        fig_mtype = px.bar(
            mag_type, x="magType", y="avg_mag",
            color="avg_mag", color_continuous_scale="Oranges",
            labels={"avg_mag": "Avg Magnitude", "magType": "Magnitude Type"},
            text_auto=".2f",
        )
        fig_mtype.update_layout(
            paper_bgcolor="#12172b", plot_bgcolor="#12172b",
            font_color="#aabbdd",
            yaxis=dict(gridcolor="#1e2640"),
            showlegend=False,
        )
        st.plotly_chart(fig_mtype, use_container_width=True)

    with c4:
        st.markdown("<div class='section-header'>Depth Category Breakdown</div>",
                    unsafe_allow_html=True)
        dep_pie = df["depth_category"].value_counts().reset_index()
        dep_pie.columns = ["depth_category", "count"]
        fig_pie = px.pie(
            dep_pie, names="depth_category", values="count",
            color="depth_category",
            color_discrete_map={
                "Shallow": "#4fc3f7", "Intermediate": "#ff9800", "Deep": "#b71c1c"
            },
            hole=0.55,
        )
        fig_pie.update_layout(
            paper_bgcolor="#12172b", font_color="#aabbdd",
            legend=dict(font=dict(color="#aabbdd")),
        )
        st.plotly_chart(fig_pie, use_container_width=True)


# ════════════════════════════════════════════
# TAB 3 – TIME TRENDS
# ════════════════════════════════════════════
with tab3:
    st.markdown("<div class='section-header'>Earthquakes Over Time</div>",
                unsafe_allow_html=True)

    monthly = (df.groupby(["year", "month"])
                 .agg(count=("id", "count"), avg_mag=("mag", "mean"))
                 .reset_index())
    monthly["date"] = pd.to_datetime(
        monthly[["year", "month"]].assign(day=1)
    )
    monthly = monthly.sort_values("date")

    fig_time = make_subplots(specs=[[{"secondary_y": True}]])
    fig_time.add_trace(
        go.Bar(x=monthly["date"], y=monthly["count"],
               name="Event Count", marker_color="#1e3a5f", opacity=0.85),
        secondary_y=False,
    )
    fig_time.add_trace(
        go.Scatter(x=monthly["date"], y=monthly["avg_mag"],
                   mode="lines", name="Avg Magnitude",
                   line=dict(color="#ff6b35", width=2)),
        secondary_y=True,
    )
    fig_time.update_layout(
        paper_bgcolor="#12172b", plot_bgcolor="#12172b",
        font_color="#aabbdd", height=380,
        legend=dict(font=dict(color="#aabbdd")),
        xaxis=dict(gridcolor="#1e2640"),
        yaxis=dict(gridcolor="#1e2640", title="Event Count"),
        yaxis2=dict(title="Avg Magnitude", overlaying="y", side="right"),
    )
    st.plotly_chart(fig_time, use_container_width=True)

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("<div class='section-header'>By Hour of Day</div>",
                    unsafe_allow_html=True)
        hourly = df.groupby("hour").size().reset_index(name="count")
        fig_hr = px.bar(
            hourly, x="hour", y="count",
            color="count", color_continuous_scale="Plasma",
            labels={"hour": "Hour (UTC)", "count": "Events"},
        )
        fig_hr.update_layout(
            paper_bgcolor="#12172b", plot_bgcolor="#12172b",
            font_color="#aabbdd", showlegend=False,
            xaxis=dict(gridcolor="#1e2640"),
            yaxis=dict(gridcolor="#1e2640"),
        )
        st.plotly_chart(fig_hr, use_container_width=True)

    with c2:
        st.markdown("<div class='section-header'>By Day of Week</div>",
                    unsafe_allow_html=True)
        day_order = ["Monday", "Tuesday", "Wednesday", "Thursday",
                     "Friday", "Saturday", "Sunday"]
        dow = (df.groupby("day_of_week").size()
                 .reindex(day_order)
                 .reset_index(name="count"))
        fig_dow = px.bar(
            dow, x="day_of_week", y="count",
            color="count", color_continuous_scale="Oranges",
        )
        fig_dow.update_layout(
            paper_bgcolor="#12172b", plot_bgcolor="#12172b",
            font_color="#aabbdd", showlegend=False,
            xaxis_title="", yaxis=dict(gridcolor="#1e2640"),
        )
        st.plotly_chart(fig_dow, use_container_width=True)

    with c3:
        st.markdown("<div class='section-header'>YoY Growth Rate</div>",
                    unsafe_allow_html=True)
        yoy = (df.groupby("year").size()
                 .reset_index(name="total"))
        yoy["growth_pct"] = yoy["total"].pct_change() * 100
        yoy.dropna(inplace=True)
        fig_yoy = px.bar(
            yoy, x="year", y="growth_pct",
            color=(yoy["growth_pct"] > 0).map({True: "Growth", False: "Decline"}),
            color_discrete_map={"Growth": "#4caf50", "Decline": "#ef5350"},
            labels={"growth_pct": "YoY Growth %", "year": "Year"},
        )
        fig_yoy.update_layout(
            paper_bgcolor="#12172b", plot_bgcolor="#12172b",
            font_color="#aabbdd", showlegend=False,
            yaxis=dict(gridcolor="#1e2640"),
        )
        st.plotly_chart(fig_yoy, use_container_width=True)

    st.markdown("<div class='section-header'>Monthly Heatmap (Count)</div>",
                unsafe_allow_html=True)
    pivot = monthly.pivot(index="year", columns="month", values="count").fillna(0)
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                   "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    fig_heat = px.imshow(
        pivot,
        labels=dict(x="Month", y="Year", color="Events"),
        x=month_names[:pivot.shape[1]],
        color_continuous_scale="YlOrRd",
        aspect="auto",
    )
    fig_heat.update_layout(
        paper_bgcolor="#12172b", font_color="#aabbdd", height=320,
    )
    st.plotly_chart(fig_heat, use_container_width=True)


# ════════════════════════════════════════════
# TAB 4 – TSUNAMIS & ALERTS
# ════════════════════════════════════════════
with tab4:
    c1, c2 = st.columns([2, 1])

    with c1:
        st.markdown("<div class='section-header'>Tsunamis Per Year</div>",
                    unsafe_allow_html=True)
        ts_yearly = (df[df["tsunami"] == 1]
                       .groupby("year").size()
                       .reset_index(name="tsunami_events"))
        fig_ts = px.bar(
            ts_yearly, x="year", y="tsunami_events",
            color="tsunami_events", color_continuous_scale="Blues",
            labels={"tsunami_events": "Tsunami Events", "year": "Year"},
            text_auto=True,
        )
        fig_ts.update_layout(
            paper_bgcolor="#12172b", plot_bgcolor="#12172b",
            font_color="#aabbdd", showlegend=False,
            yaxis=dict(gridcolor="#1e2640"),
        )
        st.plotly_chart(fig_ts, use_container_width=True)

    with c2:
        st.markdown("<div class='section-header'>Severity Distribution</div>",
                    unsafe_allow_html=True)
        sev = df["severity"].value_counts().reset_index()
        sev.columns = ["severity", "count"]
        sev_colors = {
            "Minor": "#4fc3f7", "Moderate": "#fff176",
            "Strong": "#ffb74d", "Major": "#ef5350", "Great": "#b71c1c"
        }
        fig_sev = px.funnel(
            sev, x="count", y="severity",
            color="severity", color_discrete_map=sev_colors,
        )
        fig_sev.update_layout(
            paper_bgcolor="#12172b", font_color="#aabbdd",
            showlegend=False, height=340,
        )
        st.plotly_chart(fig_sev, use_container_width=True)

    st.markdown("<div class='section-header'>Magnitude Distribution: Tsunami vs Non-Tsunami</div>",
                unsafe_allow_html=True)
    fig_box = px.box(
        df, x="tsunami", y="mag",
        color="tsunami",
        color_discrete_map={0: "#4fc3f7", 1: "#ff6b35"},
        labels={"tsunami": "Tsunami (1=Yes)", "mag": "Magnitude"},
        points=False,
    )
    fig_box.update_layout(
        paper_bgcolor="#12172b", plot_bgcolor="#12172b",
        font_color="#aabbdd", showlegend=False,
        yaxis=dict(gridcolor="#1e2640"),
    )
    st.plotly_chart(fig_box, use_container_width=True)

    st.markdown("<div class='section-header'>Top Countries – Tsunami Earthquakes</div>",
                unsafe_allow_html=True)
    ts_country = (df[df["tsunami"] == 1]
                    .groupby("country")
                    .agg(tsunami_count=("tsunami", "sum"),
                         avg_mag=("mag", "mean"))
                    .sort_values("tsunami_count", ascending=False)
                    .head(15)
                    .reset_index())
    fig_tsc = px.bar(
        ts_country, x="country", y="tsunami_count",
        color="avg_mag", color_continuous_scale="Inferno",
        labels={"tsunami_count": "Tsunami Events", "country": "Country"},
        text_auto=True,
    )
    fig_tsc.update_layout(
        paper_bgcolor="#12172b", plot_bgcolor="#12172b",
        font_color="#aabbdd",
        yaxis=dict(gridcolor="#1e2640"),
        xaxis_tickangle=-40,
    )
    st.plotly_chart(fig_tsc, use_container_width=True)


# ════════════════════════════════════════════
# TAB 5 – ADVANCED ANALYTICS
# ════════════════════════════════════════════
with tab5:

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("<div class='section-header'>Top 20 Most Active Countries</div>",
                    unsafe_allow_html=True)
        country_stats = (df.groupby("country")
                           .agg(count=("id", "count"),
                                avg_mag=("mag", "mean"),
                                avg_depth=("depth_km", "mean"))
                           .sort_values("count", ascending=False)
                           .head(20)
                           .reset_index())
        fig_ctry = px.bar(
            country_stats, x="count", y="country", orientation="h",
            color="avg_mag", color_continuous_scale="Plasma",
            labels={"count": "Event Count", "country": ""},
            text_auto=True,
        )
        fig_ctry.update_layout(
            paper_bgcolor="#12172b", plot_bgcolor="#12172b",
            font_color="#aabbdd", height=520,
            yaxis=dict(autorange="reversed"),
            xaxis=dict(gridcolor="#1e2640"),
        )
        st.plotly_chart(fig_ctry, use_container_width=True)

    with c2:
        st.markdown("<div class='section-header'>Activity Score (Freq × Avg Mag)</div>",
                    unsafe_allow_html=True)
        country_stats["activity_score"] = (
            country_stats["count"] * country_stats["avg_mag"]
        )
        top20_act = country_stats.sort_values("activity_score", ascending=False).head(15)
        fig_act = px.treemap(
            top20_act, path=["country"], values="activity_score",
            color="avg_mag", color_continuous_scale="Inferno",
            labels={"activity_score": "Activity Score", "avg_mag": "Avg Magnitude"},
        )
        fig_act.update_layout(
            paper_bgcolor="#12172b", font_color="#aabbdd", height=520,
        )
        st.plotly_chart(fig_act, use_container_width=True)

    st.markdown("<div class='section-header'>Data Quality: Gap vs RMS by Country</div>",
                unsafe_allow_html=True)
    quality = (df.groupby("country")
                 .agg(avg_gap=("gap", "mean"),
                      avg_rms=("rms", "mean"),
                      count=("id", "count"))
                 .query("count >= 20")
                 .reset_index())
    fig_qual = px.scatter(
        quality, x="avg_gap", y="avg_rms",
        size="count", color="avg_gap",
        color_continuous_scale="Reds",
        hover_name="country",
        labels={"avg_gap": "Avg Gap (°)", "avg_rms": "Avg RMS"},
        size_max=40,
    )
    fig_qual.update_layout(
        paper_bgcolor="#12172b", plot_bgcolor="#12172b",
        font_color="#aabbdd", height=420,
        xaxis=dict(gridcolor="#1e2640"),
        yaxis=dict(gridcolor="#1e2640"),
    )
    st.plotly_chart(fig_qual, use_container_width=True)

    st.markdown("<div class='section-header'>Shallow-to-Deep Ratio by Country</div>",
                unsafe_allow_html=True)
    shallow_deep = (df.groupby(["country", "depth_category"])
                      .size()
                      .unstack(fill_value=0)
                      .reset_index())
    if "Shallow" in shallow_deep.columns and "Deep" in shallow_deep.columns:
        shallow_deep["ratio"] = (
            shallow_deep["Shallow"] /
            (shallow_deep["Deep"] + 0.001)
        )
        top_ratio = shallow_deep.query("Deep > 5").sort_values("ratio", ascending=False).head(15)
        fig_ratio = px.bar(
            top_ratio, x="country", y="ratio",
            color="ratio", color_continuous_scale="Turbo",
            labels={"ratio": "Shallow/Deep Ratio"},
            text_auto=".1f",
        )
        fig_ratio.update_layout(
            paper_bgcolor="#12172b", plot_bgcolor="#12172b",
            font_color="#aabbdd",
            yaxis=dict(gridcolor="#1e2640"),
            xaxis_tickangle=-45,
            showlegend=False,
        )
        st.plotly_chart(fig_ratio, use_container_width=True)

    # Raw data explorer
    st.markdown("<div class='section-header'>Raw Data Explorer</div>",
                unsafe_allow_html=True)
    n_rows = st.slider("Rows to preview", 50, 1000, 200, step=50)
    cols_to_show = st.multiselect(
        "Select columns",
        df.columns.tolist(),
        default=["time", "place", "country", "mag", "depth_km",
                 "severity", "depth_category", "tsunami"],
    )
    st.dataframe(df[cols_to_show].head(n_rows), use_container_width=True)
    st.caption(f"Showing {min(n_rows, len(df)):,} of {len(df):,} filtered rows.")
