# Geospatial Analytics Portfolio

**Hetvi Chavda** — MS Data Analytics Engineering, Northeastern University

Two end-to-end geospatial analytics projects in Python. Each loads a Census TIGER/Line shapefile, performs a spatial merge with public socioeconomic or patent data, and ships an interactive Streamlit dashboard.

---

## Middlesex County ZCTA Livability Dashboard

Scores all 100 ZIP Code Tabulation Areas in Middlesex County, MA on a composite livability index built from five ACS indicators: median household income, education attainment, home value, commute time, and population density. Each ZCTA receives a normalised 0–100 score and letter grade so residents and planners can compare neighbourhoods on equal footing.

![Geographic distribution of livability scores across Middlesex County](middlesex_livability/screenshots/geographic_distribution.png)

![Dashboard overview with key metrics and composite score rankings](middlesex_livability/screenshots/dashboard_overview.png)

**Highlights**
- Cambridge (02139) and Wellesley (02481) tied #1 at 73.8 — Cambridge leads on education (76.6% Bach+), Wellesley on income ($227,898)
- Lawrence (01840) ranks last at 10.2 — lowest income in the county, highest population density
- Wealthy outer suburbs score lowest on commute despite high incomes, breaking the income–quality-of-life assumption
- Two ZCTAs with Census suppression codes (−666666666) were filled with county medians rather than dropped, preserving 100 ZCTAs in the analysis

**Stack:** Python · GeoPandas · Plotly · Streamlit
**Data:** ACS 5-Year 2020 (Census API) · TIGER/Line ZCTA boundaries

```bash
cd middlesex_livability
streamlit run Middlesex_app.py
```

---

## USPTO Patent Choropleth Map

Maps utility patent grant activity across all 50 U.S. states and DC using USPTO CBSA data for 2015, with two choropleth views — raw count and per-capita rate — to surface the key finding that California's raw dominance looks completely different once population is factored in.

![Raw patent count choropleth — California leads with 40,134 grants](uspto_patent_map/screenshots/raw_patent_count.png)

![State rankings: raw count vs. per-capita rate side by side](uspto_patent_map/screenshots/state_rankings.png)

**Highlights**
- California leads raw volume at 40,134 patents — nearly 4× the next state (New York, 12,244)
- DC leads per capita at 343.6 per 100k — federal research institutions concentrated in a tiny geography
- Massachusetts ranks top-3 per capita at 100.8, driven by the Boston-Cambridge biotech corridor
- San Jose metro alone produced 14,618 patents — more than most entire states

**Stack:** Python · GeoPandas · Plotly · Streamlit
**Data:** USPTO Utility Patent Grants 2015 · TIGER/Line state boundaries · Census 2015 population estimates

```bash
cd uspto_patent_map
streamlit run uspto_app.py
```

---

## Setup

```bash
pip install -r requirements.txt
```

Census API key (free): https://api.census.gov/data/key_signup.html

Shapefiles are gitignored due to size:
- ZCTA: https://www2.census.gov/geo/tiger/GENZ2020/shp/cb_2020_us_zcta520_500k.zip
- States: https://www2.census.gov/geo/tiger/TIGER2020/STATE/tl_2020_us_state.zip
