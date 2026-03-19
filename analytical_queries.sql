-- ═══════════════════════════════════════════════════════════════
-- Global Seismic Trends – Analytical SQL Queries
-- Database: seismic_db  |  Table: earthquakes
-- ═══════════════════════════════════════════════════════════════

USE seismic_db;


-- ───────────────────────────────────────────────────────────────
-- MAGNITUDE & DEPTH
-- ───────────────────────────────────────────────────────────────

-- Q1. Top 10 Strongest Earthquakes
SELECT id, place, country, time, mag, depth_km, severity
FROM earthquakes
ORDER BY mag DESC
LIMIT 10;

-- Q2. Top 10 Deepest Earthquakes
SELECT id, place, country, time, mag, depth_km, depth_category
FROM earthquakes
ORDER BY depth_km DESC
LIMIT 10;

-- Q3. Shallow & Powerful – depth < 50 km AND mag > 7.5
SELECT id, place, country, time, mag, depth_km
FROM earthquakes
WHERE depth_km < 50
  AND mag > 7.5
ORDER BY mag DESC;

-- Q4. Average Depth per Continent (proxy: country group)
--     NOTE: add a `continent` column if needed; using country here
SELECT country,
       ROUND(AVG(depth_km), 2)  AS avg_depth_km,
       COUNT(*)                 AS event_count
FROM earthquakes
GROUP BY country
HAVING event_count >= 10
ORDER BY avg_depth_km DESC
LIMIT 20;

-- Q5. Average Magnitude per Magnitude Type
SELECT magType,
       ROUND(AVG(mag), 3) AS avg_mag,
       COUNT(*)           AS event_count
FROM earthquakes
GROUP BY magType
ORDER BY avg_mag DESC;


-- ───────────────────────────────────────────────────────────────
-- TIME ANALYSIS
-- ───────────────────────────────────────────────────────────────

-- Q6. Year with Most Earthquakes
SELECT year,
       COUNT(*) AS total_events
FROM earthquakes
GROUP BY year
ORDER BY total_events DESC
LIMIT 1;

-- Q7. Month with Highest Number of Earthquakes
SELECT month,
       MONTHNAME(STR_TO_DATE(CONCAT('2000-', month, '-01'), '%Y-%m-%d')) AS month_name,
       COUNT(*) AS total_events
FROM earthquakes
GROUP BY month
ORDER BY total_events DESC
LIMIT 1;

-- Q8. Day of Week with Most Earthquakes
SELECT day_of_week,
       COUNT(*) AS total_events
FROM earthquakes
GROUP BY day_of_week
ORDER BY total_events DESC;

-- Q9. Count of Earthquakes per Hour of Day
SELECT hour,
       COUNT(*) AS total_events
FROM earthquakes
GROUP BY hour
ORDER BY hour;

-- Q10. Most Active Reporting Network
SELECT net,
       COUNT(*) AS reported_events
FROM earthquakes
GROUP BY net
ORDER BY reported_events DESC
LIMIT 10;


-- ───────────────────────────────────────────────────────────────
-- CASUALTIES & ECONOMIC LOSS
-- (sig used as proxy for impact; add real econ/casualty cols if available)
-- ───────────────────────────────────────────────────────────────

-- Q11. Top 5 Places with Highest Impact (sig as proxy)
SELECT place, country,
       SUM(sig) AS total_significance,
       MAX(mag) AS max_magnitude,
       COUNT(*) AS event_count
FROM earthquakes
GROUP BY place, country
ORDER BY total_significance DESC
LIMIT 5;

-- Q12. Total Significance Score per Country (econ-loss proxy)
SELECT country,
       SUM(sig)       AS total_sig,
       ROUND(AVG(mag), 2) AS avg_mag,
       COUNT(*)       AS event_count
FROM earthquakes
GROUP BY country
ORDER BY total_sig DESC
LIMIT 20;

-- Q13. Average Significance by Severity Level (alert-level proxy)
SELECT severity,
       ROUND(AVG(sig), 1) AS avg_sig,
       COUNT(*)           AS event_count
FROM earthquakes
GROUP BY severity
ORDER BY avg_sig DESC;


-- ───────────────────────────────────────────────────────────────
-- EVENT TYPE & QUALITY METRICS
-- ───────────────────────────────────────────────────────────────

-- Q14. Reviewed vs Automatic Earthquakes
SELECT status,
       COUNT(*) AS count,
       ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS pct
FROM earthquakes
GROUP BY status;

-- Q15. Count by Earthquake Type
SELECT type,
       COUNT(*) AS count
FROM earthquakes
GROUP BY type
ORDER BY count DESC;

-- Q16. Number of Earthquakes by Data Type (parsed from types field)
--      types is comma-separated; we count events containing each keyword
SELECT
    SUM(CASE WHEN types LIKE '%shakemap%'   THEN 1 ELSE 0 END) AS has_shakemap,
    SUM(CASE WHEN types LIKE '%dyfi%'       THEN 1 ELSE 0 END) AS has_dyfi,
    SUM(CASE WHEN types LIKE '%phase-data%' THEN 1 ELSE 0 END) AS has_phase_data,
    SUM(CASE WHEN types LIKE '%moment-tensor%' THEN 1 ELSE 0 END) AS has_moment_tensor,
    SUM(CASE WHEN types LIKE '%focal-mechanism%' THEN 1 ELSE 0 END) AS has_focal_mechanism
FROM earthquakes;

-- Q17. Average RMS and Gap per Country
SELECT country,
       ROUND(AVG(rms), 4)  AS avg_rms,
       ROUND(AVG(gap), 2)  AS avg_gap,
       COUNT(*)            AS event_count
FROM earthquakes
GROUP BY country
HAVING event_count >= 10
ORDER BY avg_gap ASC
LIMIT 20;

-- Q18. Events with High Station Coverage (nst > 50)
SELECT id, place, country, time, mag, nst
FROM earthquakes
WHERE nst > 50
ORDER BY nst DESC
LIMIT 20;


-- ───────────────────────────────────────────────────────────────
-- TSUNAMIS & ALERTS
-- ───────────────────────────────────────────────────────────────

-- Q19. Number of Tsunamis Triggered per Year
SELECT year,
       SUM(tsunami) AS tsunami_events,
       COUNT(*)     AS total_events,
       ROUND(SUM(tsunami) * 100.0 / COUNT(*), 2) AS tsunami_pct
FROM earthquakes
GROUP BY year
ORDER BY year;

-- Q20. Count Earthquakes by Severity (acting as alert-level proxy)
SELECT severity,
       COUNT(*) AS event_count
FROM earthquakes
GROUP BY severity
ORDER BY FIELD(severity, 'Great', 'Major', 'Strong', 'Moderate', 'Minor');


-- ───────────────────────────────────────────────────────────────
-- SEISMIC PATTERN & TRENDS ANALYSIS
-- ───────────────────────────────────────────────────────────────

-- Q21. Top 5 Countries with Highest Average Magnitude (past 10 years)
SELECT country,
       ROUND(AVG(mag), 3) AS avg_mag,
       COUNT(*)           AS event_count
FROM earthquakes
WHERE year >= YEAR(CURDATE()) - 10
GROUP BY country
HAVING event_count >= 20
ORDER BY avg_mag DESC
LIMIT 5;

-- Q22. Countries with Both Shallow AND Deep Earthquakes in Same Month
SELECT country, year, month,
       SUM(CASE WHEN depth_category = 'Shallow' THEN 1 ELSE 0 END) AS shallow_count,
       SUM(CASE WHEN depth_category = 'Deep'    THEN 1 ELSE 0 END) AS deep_count
FROM earthquakes
GROUP BY country, year, month
HAVING shallow_count > 0
   AND deep_count > 0
ORDER BY country, year, month;

-- Q23. Year-over-Year Growth Rate in Total Earthquakes
WITH yearly AS (
    SELECT year, COUNT(*) AS total
    FROM earthquakes
    GROUP BY year
),
yoy AS (
    SELECT year,
           total,
           LAG(total) OVER (ORDER BY year) AS prev_total
    FROM yearly
)
SELECT year,
       total,
       prev_total,
       ROUND((total - prev_total) * 100.0 / NULLIF(prev_total, 0), 2) AS yoy_growth_pct
FROM yoy
ORDER BY year;

-- Q24. Top 3 Most Seismically Active Regions (frequency × avg magnitude)
SELECT country,
       COUNT(*)           AS frequency,
       ROUND(AVG(mag), 3) AS avg_mag,
       ROUND(COUNT(*) * AVG(mag), 1) AS activity_score
FROM earthquakes
GROUP BY country
HAVING frequency >= 50
ORDER BY activity_score DESC
LIMIT 3;


-- ───────────────────────────────────────────────────────────────
-- DEPTH, LOCATION & DISTANCE-BASED ANALYSIS
-- ───────────────────────────────────────────────────────────────

-- Q25. Average Depth Within ±5° Latitude of Equator (per country)
SELECT country,
       ROUND(AVG(depth_km), 2) AS avg_equatorial_depth,
       COUNT(*)                AS event_count
FROM earthquakes
WHERE latitude BETWEEN -5 AND 5
GROUP BY country
HAVING event_count >= 5
ORDER BY avg_equatorial_depth DESC;

-- Q26. Countries with Highest Shallow-to-Deep Ratio
SELECT country,
       SUM(CASE WHEN depth_category = 'Shallow' THEN 1 ELSE 0 END) AS shallow,
       SUM(CASE WHEN depth_category = 'Deep'    THEN 1 ELSE 0 END) AS deep,
       ROUND(
           SUM(CASE WHEN depth_category = 'Shallow' THEN 1 ELSE 0 END) /
           NULLIF(SUM(CASE WHEN depth_category = 'Deep' THEN 1 ELSE 0 END), 0),
       2) AS shallow_to_deep_ratio
FROM earthquakes
GROUP BY country
HAVING deep > 0 AND shallow > 10
ORDER BY shallow_to_deep_ratio DESC
LIMIT 15;

-- Q27. Average Magnitude Difference: Tsunami vs Non-Tsunami
SELECT
    tsunami,
    ROUND(AVG(mag), 3) AS avg_mag,
    COUNT(*)           AS event_count
FROM earthquakes
GROUP BY tsunami;

-- Cleaner diff view
SELECT
    ROUND(
        MAX(CASE WHEN tsunami = 1 THEN avg_mag END) -
        MAX(CASE WHEN tsunami = 0 THEN avg_mag END),
    3) AS mag_diff_tsunami_vs_not
FROM (
    SELECT tsunami, ROUND(AVG(mag), 3) AS avg_mag
    FROM earthquakes GROUP BY tsunami
) t;

-- Q28. Lowest Data Reliability Events (highest gap & rms)
SELECT id, place, country, time, mag,
       gap, rms,
       ROUND((gap * 0.6 + rms * 100 * 0.4), 2) AS reliability_error_score
FROM earthquakes
WHERE gap IS NOT NULL AND rms IS NOT NULL
ORDER BY reliability_error_score DESC
LIMIT 20;

-- Q29. Pairs of Consecutive Earthquakes Within ~50 km and 1 Hour
--      Uses Haversine approximation via lat/lon differences
WITH ordered AS (
    SELECT *,
           LAG(time)      OVER (ORDER BY time) AS prev_time,
           LAG(latitude)  OVER (ORDER BY time) AS prev_lat,
           LAG(longitude) OVER (ORDER BY time) AS prev_lon,
           LAG(id)        OVER (ORDER BY time) AS prev_id
    FROM earthquakes
),
filtered AS (
    SELECT id, prev_id, time, prev_time,
           place, latitude, longitude, mag,
           TIMESTAMPDIFF(MINUTE, prev_time, time) AS minutes_apart,
           -- Great-circle distance approximation in km
           111.045 * DEGREES(ACOS(LEAST(1.0,
               COS(RADIANS(latitude))  * COS(RADIANS(prev_lat)) *
               COS(RADIANS(longitude) - RADIANS(prev_lon)) +
               SIN(RADIANS(latitude))  * SIN(RADIANS(prev_lat))
           ))) AS distance_km
    FROM ordered
    WHERE prev_time IS NOT NULL
)
SELECT id, prev_id, time, minutes_apart,
       ROUND(distance_km, 2) AS distance_km, mag, place
FROM filtered
WHERE minutes_apart BETWEEN 0 AND 60
  AND distance_km   <= 50
ORDER BY distance_km;

-- Q30. Regions with Highest Frequency of Deep-Focus Earthquakes (depth > 300 km)
SELECT country,
       COUNT(*) AS deep_focus_events,
       ROUND(AVG(mag), 3) AS avg_mag,
       ROUND(AVG(depth_km), 1) AS avg_depth
FROM earthquakes
WHERE depth_km > 300
GROUP BY country
HAVING deep_focus_events >= 5
ORDER BY deep_focus_events DESC
LIMIT 15;
