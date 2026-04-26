
# Geospatial Analytics Portfolio
Hetvi Chavda — MS Data Analytics Engineering, Northeastern University

This repository brings together two geospatial analytics projects built in Python. One focuses on evaluating livability across ZIP codes in Middlesex County using socioeconomic data, while the other explores how innovation is distributed across the U.S. through patent activity. Both projects combine spatial data with public datasets and present the results through interactive Streamlit dashboards.

---

## Projects

### 1. Middlesex County ZCTA Livability Dashboard

This dashboard evaluates all 100 ZIP Code Tabulation Areas in Middlesex County, MA using a composite livability index built from five ACS indicators:

- Median household income
- Educational attainment
- Median home value
- Mean commute time
- Population density

Each ZCTA receives a normalized 0–100 score and letter grade.

---

![Geographic distribution of livability scores across Middlesex County](middlesex_livability/screenshots/geographic_distribution.png)

![Dashboard overview with key metrics and composite score rankings](middlesex_livability/screenshots/dashboard_overview.png)

**Key Findings**
- Cambridge (02139) and Wellesley (02481) tied for the top spot at 73.8. Cambridge leads in education (76.6% Bachelor’s+), while Wellesley leads in income ($227,898)
- Lawrence (01840) ranks last at 10.2, with the lowest income and highest population density in the county
- Some high-income suburbs score low on commute time, showing that income alone does not define livability
- Census suppression values were imputed using county medians to preserve all 100 ZCTAs in the analysis
- 
**Tech Stack:** Python · GeoPandas · Plotly · Streamlit  
**Data Source:** ACS 5-Year 2020 (Census API) · TIGER/Line ZCTA boundaries

```bash
cd middlesex_livability
streamlit run Middlesex_app.py
```
The dashboard allows users to explore spatial patterns and compare livability scores interactively across the county.

---

### 2. USPTO Patent Choropleth Map

This project maps utility patent activity across all 50 U.S. states and DC using USPTO data from 2015. It includes two views, total patent counts and per-capita rates, to show how the geography of innovation changes depending on how it is measured.

![Raw patent count choropleth — California leads with 40,134 grants](uspto_patent_map/screenshots/raw_patent_count.png)

![State rankings: raw count vs. per-capita rate side by side](uspto_patent_map/screenshots/state_rankings.png)


**Key Findings**
- California leads raw volume at 40,134 patents, nearly 4x New York (12,244)
- DC ranks highest per capita at 343.6 per 100k, reflecting a dense concentration of research institutions
- Massachusetts ranks top-3 per capita at 100.8, driven by the Boston Cambridge innovation corridor
- San Jose metro alone produced 14,618 patents, more than most entire states

**Tech Stack:** Python · GeoPandas · Plotly · Streamlit  
**Data Sources:** USPTO Utility Patent Grants 2015 · TIGER/Line state boundaries · Census 2015 population estimates

```bash
cd uspto_patent_map
streamlit run uspto_app.py
```

---

## Clone & Setup

```bash
git clone https://github.com/HAC-11/Portfolio-Demos-.git
cd Portfolio-Demos-
pip install -r requirements.txt
```

Census API key (free): https://api.census.gov/data/key_signup.html

Shapefiles not included due to size:
- ZCTA: https://www2.census.gov/geo/tiger/GENZ2020/shp/cb_2020_us_zcta520_500k.zip
- States: https://www2.census.gov/geo/tiger/TIGER2020/STATE/tl_2020_us_state.zip
