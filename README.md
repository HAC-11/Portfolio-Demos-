# Geospatial Analytics Portfolio
Hetvi Chavda · MS Data Analytics Engineering · Northeastern University · Boston, MA

---

## Overview

Two end-to-end geospatial analytics projects built with Python, GeoPandas, Plotly, and real U.S. government datasets. Both follow the same core pipeline: load Census TIGER/Line shapefiles with GeoPandas, perform a spatial merge with socioeconomic or patent data, and produce interactive visualisations that surface patterns invisible in raw tables.

---

## Project 1 — Middlesex County ZCTA Livability Dashboard

Analyses livability across 100 ZIP Code Tabulation Areas in Middlesex County, Massachusetts using five ACS indicators: median household income, education attainment, median home value, commute time, and population density. Each ZCTA receives a normalised composite livability score (0–100) and letter grade (A–D).

**Stack:** Python · GeoPandas · Plotly · Pandas

**Data:** U.S. Census Bureau ACS 5-Year 2020 · Census TIGER/Line ZCTA Boundaries

**Pipeline:**
- Fetched ACS indicators for 100 Middlesex ZCTAs via Census API (B19013, B25077, B08136, B15003)
- Loaded Census TIGER/Line ZCTA shapefile (cb_2020_us_zcta520_500k) with GeoPandas
- Reprojected to EPSG:4326 (WGS84) for Plotly compatibility
- Performed spatial merge using ZCTA5CE20 as join key (confirmed from DBF header)
- Normalised all five indicators to 0–100 scale, computed equal-weighted composite score
- Built interactive choropleth map, radar chart, bar chart, and scatter plot with Plotly

**Key Findings:**
- Cambridge (02139) and Wellesley (02481) tied #1 at 73.8 — Cambridge leads Education; Wellesley leads Income ($227,898)
- Lawrence (01840) ranks last at 10.2 — lowest income, highest density
- High home values do not guarantee short commutes — wealthy outer suburbs score lowest on commute

**Technical notes:**
- Commute derived from B08136 / B08101 — B08303 stores bands not a mean (common mistake avoided)
- 2 ZCTAs with Census N/A code (-666666666) filled with county median rather than dropped
- Spatial join cached in Streamlit deployment via @st.cache_data — 35% reduction in processing time
- Plotly radar fill colours use rgba() format — appending opacity to hex raises ValueError

---

## Project 2 — USPTO Patent Choropleth Map

Analyses utility patent grant activity across all 50 U.S. states and DC using USPTO CBSA metropolitan area data for 2015. Builds two choropleth views — raw patent count and per-capita rate — to surface the key insight that California's raw dominance looks very different once population is accounted for.

**Stack:** Python · GeoPandas · Matplotlib · Plotly · Pandas

**Data:** USPTO Utility Patent Grants 2015 · Census TIGER/Line State Boundaries · Census 2015 Population Estimates

**Pipeline:**
- Parsed USPTO CBSA bulk file — extracted primary state from MSA name string
- Loaded Census TIGER/Line state shapefile (tl_2020_us_state) with GeoPandas
- Confirmed STUSPS as state abbreviation column from DBF header before writing merge code
- Performed spatial merge on STUSPS join key
- Computed per-capita rate using 2015 Census population estimates
- Built Matplotlib static choropleth (EPSG:5070 Albers Equal Area) and Plotly interactive maps

**Key Findings:**
- California leads raw volume (40,134 patents) — nearly 4x the next state
- DC leads per capita (343.6 per 100K) — federal research institutions in a small geography
- Massachusetts ranks top-3 per capita (100.8) — Boston-Cambridge biotech corridor
- San Jose metro alone produced 14,618 patents — more than most entire states
- Raw counts and per-capita rates tell completely different stories about American innovation

**Technical notes:**
- Multi-state metros assigned to first-listed state — documented limitation
- EPSG:5070 used for Matplotlib static map (standard for U.S. thematic cartography)
- Per-capita denominator matched to 2015 to align with grant year

---

## Files

middlesex_livability/
- Middlesex_ZCTA_Livability_Dashboard.ipynb — full Python notebook
- Middlesex_County_ZCTA_Analysis_Full.xlsx — 100-ZCTA dataset from Census API
- Middlesex_Livability_Dashboard.html — standalone interactive dashboard

uspto_patent_map/
- USPTO_Patent_Choropleth_Map.ipynb — full Python notebook
- Patents.csv — USPTO CBSA patent grant data
- USPTO_Patent_Map.html — standalone interactive dashboard

Note: Census TIGER/Line shapefiles not included due to file size.

Download ZCTA boundaries: https://www2.census.gov/geo/tiger/GENZ2020/shp/cb_2020_us_zcta520_500k.zip

Download state boundaries: https://www2.census.gov/geo/tiger/TIGER2020/STATE/tl_2020_us_state.zip

---

## Setup

pip install geopandas pandas plotly matplotlib openpyxl requests jupyter

Census API key (free, instant): https://api.census.gov/data/key_signup.html

---

## Data Sources

- ACS 5-Year Estimates: Census Bureau 2020 via API
- ZCTA Boundaries: Census TIGER/Line cb_2020_us_zcta520_500k
- State Boundaries: Census TIGER/Line tl_2020_us_state
- Patent Grants: USPTO CBSA Utility Patent Files 2015
- Population Estimates: Census Bureau 2015

---

