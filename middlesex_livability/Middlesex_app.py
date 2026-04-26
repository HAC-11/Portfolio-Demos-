"""
Middlesex County ZCTA Livability Dashboard
Hetvi Chavda · MS Data Analytics Engineering · Northeastern University

Run:
    streamlit run app.py

Files required (same folder):
    Middlesex_County_ZCTA_Analysis_Full.xlsx
    cb_2020_us_zcta520_500k/cb_2020_us_zcta520_500k.shp (+ .dbf .shx .prj .cpg)
"""

import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.graph_objects as go
import plotly.express as px
import json
import warnings
warnings.filterwarnings("ignore")

# ── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Middlesex County · ZCTA Livability",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background-color: #0c0f0a; }
    [data-testid="stSidebar"] { background-color: #131710; border-right: 1px solid #2a3025; }
    [data-testid="stSidebar"] * { color: #eef2ea !important; }
    h1, h2, h3 { color: #eef2ea !important; }
    p, li { color: #7a8a72; }
    .stMetric { background: #131710; border: 1px solid #2a3025; border-radius: 8px; padding: 12px; }
    .stMetric label { color: #7a8a72 !important; font-size: 11px !important; }
    .stMetric [data-testid="stMetricValue"] { color: #4ade80 !important; }
    div[data-testid="stSelectbox"] label { color: #7a8a72 !important; }
    .stDataFrame { background: #131710; }
    footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── CONSTANTS ────────────────────────────────────────────────────────────────
ZCTA_TOWN_MAP = {
    "01701":"Framingham","01702":"Framingham","01718":"Acton","01719":"Boxborough",
    "01720":"Acton","01721":"Ashland","01730":"Bedford","01731":"Hanscom AFB",
    "01740":"Bolton","01741":"Carlisle","01742":"Concord","01745":"Holliston",
    "01746":"Holliston","01747":"Hopedale","01748":"Hopkinton","01749":"Hudson",
    "01752":"Marlborough","01754":"Maynard","01756":"Millbury","01757":"Milford",
    "01760":"Natick","01770":"Sherborn","01772":"Southborough","01773":"Lincoln",
    "01775":"Stow","01776":"Sudbury","01778":"Wayland","01801":"Woburn",
    "01803":"Burlington","01810":"Andover","01821":"Billerica","01824":"Chelmsford",
    "01826":"Dracut","01827":"Dunstable","01830":"Haverhill","01832":"Haverhill",
    "01833":"Georgetown","01834":"Groveland","01835":"Haverhill","01840":"Lawrence",
    "01841":"Lawrence","01843":"Lawrence","01844":"Methuen","01845":"N. Andover",
    "01850":"Lowell","01851":"Lowell","01852":"Lowell","01854":"Lowell",
    "01860":"Merrimac","01862":"N. Billerica","01863":"N. Chelmsford",
    "01864":"N. Reading","01867":"Reading","01876":"Tewksbury","01879":"Tyngsborough",
    "01880":"Wakefield","01886":"Westford","01887":"Wilmington","01890":"Winchester",
    "02138":"Cambridge","02139":"Cambridge","02140":"Cambridge","02141":"Cambridge",
    "02142":"Cambridge","02143":"Somerville","02144":"Somerville","02145":"Somerville",
    "02148":"Malden","02149":"Everett","02150":"Chelsea","02151":"Revere",
    "02152":"Winthrop","02155":"Medford","02163":"Cambridge","02176":"Melrose",
    "02180":"Stoneham","02420":"Lexington","02421":"Lexington","02451":"Waltham",
    "02452":"Waltham","02453":"Waltham","02458":"Newton","02459":"Newton",
    "02460":"Newton","02461":"Newton","02462":"Newton","02464":"Newton",
    "02465":"Newton","02466":"Newton","02467":"Newton","02468":"Newton",
    "02472":"Watertown","02474":"Arlington","02476":"Arlington","02478":"Belmont",
    "02481":"Wellesley","02482":"Wellesley","02492":"Needham","02493":"Weston",
    "02494":"Needham"
}

SCORE_COLS  = ["Income_Score","Education_Score","HomeValue_Score","Commute_Score","Density_Score"]
SCORE_NAMES = ["Income","Education","Home Value","Commute","Density"]

PALETTE_RGBA = [
    ("rgba(27,94,32,0.15)",   "#1B5E20"),
    ("rgba(21,101,192,0.15)", "#1565C0"),
    ("rgba(183,28,28,0.15)",  "#B71C1C"),
    ("rgba(230,81,0,0.15)",   "#E65100"),
    ("rgba(74,21,150,0.15)",  "#4A148C"),
    ("rgba(0,96,100,0.15)",   "#006064"),
    ("rgba(85,139,47,0.15)",  "#558B2F"),
    ("rgba(55,71,79,0.15)",   "#37474F"),
    ("rgba(78,52,46,0.15)",   "#4E342E"),
    ("rgba(136,14,79,0.15)",  "#880E4F"),
]

def grade_color(s):
    return "#1B5E20" if s>=70 else "#43A047" if s>=50 else "#F9A825" if s>=35 else "#E53935"

def grade(s):
    return "A" if s>=70 else "B" if s>=50 else "C" if s>=35 else "D"

def hex_to_rgba(hex_color, opacity=0.13):
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
    return f"rgba({r},{g},{b},{opacity})"

PLOTLY_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="sans-serif", color="#7a8a72", size=12),
)

# ── DATA LOADING ─────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_excel("Middlesex_County_ZCTA_Analysis_Full.xlsx")
    df["ZCTA_str"]  = df["ZCTA"].astype(str).str.zfill(5)
    df["Town"]      = df["ZCTA_str"].map(ZCTA_TOWN_MAP).fillna("Middlesex County")
    df["Label"]     = df["Town"] + " (" + df["ZCTA_str"] + ")"
    df["Grade"]     = df["Composite_Score"].apply(grade)
    df["Grade_Color"] = df["Composite_Score"].apply(grade_color)
    return df

@st.cache_data
def load_geodata(_df):
    """
    Load Census ZCTA shapefile with GeoPandas, reproject, filter,
    spatial merge, and build GeoJSON for Plotly choropleth.
    Cached so the expensive operation runs only once.
    """
    try:
        gdf = gpd.read_file("middlesex_livability/cb_2020_us_zcta520_500k/cb_2020_us_zcta520_500k.shp")
        gdf = gdf.to_crs(epsg=4326)
        zctas = _df["ZCTA_str"].tolist()
        gdf_mx = gdf[gdf["ZCTA5CE20"].isin(zctas)].copy()
        gdf_mx = gdf_mx.rename(columns={"ZCTA5CE20": "ZCTA_str"})

        merge_cols = [
            "ZCTA_str","Town","Label","Composite_Score","Grade","Grade_Color",
            "Median_Income","Median_Home_Value","Mean_Commute","Pct_Bachelors",
            "Population","Pop_Density","Rank",
            "Income_Score","Education_Score","HomeValue_Score","Commute_Score","Density_Score"
        ]
        merged = gdf_mx.merge(_df[merge_cols], on="ZCTA_str", how="left")
        merged["Population"]    = merged["Population"].fillna(0).astype(int)
        merged["Median_Income"] = merged["Median_Income"].fillna(0).astype(int)

        geojson = json.loads(merged.to_json())
        for feat in geojson["features"]:
            feat["id"] = feat["properties"]["ZCTA_str"]

        return merged, geojson

    except FileNotFoundError:
        return None, None

# ── LOAD ─────────────────────────────────────────────────────────────────────
df = load_data()
merged_gdf, geojson = load_geodata(df)

# ── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## Middlesex County")
    st.markdown("---")
    page = st.radio(
        "View",
        ["Overview", "Map", "Compare", "Indicators", "Data"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    st.markdown(f"**{len(df)} ZCTAs** · ACS 5-Year 2020")
    st.markdown("GeoPandas · Plotly · Streamlit")
    st.markdown("---")
    st.markdown("**Hetvi Chavda**  \nNortheastern University")

# ── HEADER ───────────────────────────────────────────────────────────────────
st.markdown("""
<div style="padding:28px 0 20px">
  <p style="font-family:monospace;font-size:10px;letter-spacing:3px;
            text-transform:uppercase;color:#4ade80;opacity:.75;margin-bottom:10px">
    Middlesex County, MA · ACS 5-Year 2020
  </p>
  <h1 style="font-size:32px;margin-bottom:0;color:#eef2ea">
    ZCTA Livability Dashboard
  </h1>
</div>
""", unsafe_allow_html=True)

# KPIs
top = df.loc[df["Composite_Score"].idxmax()]
bot = df.loc[df["Composite_Score"].idxmin()]
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("ZCTAs", len(df))
c2.metric("Indicators", 5)
c3.metric("Top Score", f"{top['Composite_Score']:.1f}")
c4.metric("Top ZCTA", top["Town"])
c5.metric("Bottom ZCTA", bot["Town"])

st.markdown("---")

# ═══════════════════════════════════════════════════════════════
# PAGE: OVERVIEW
# ═══════════════════════════════════════════════════════════════
if page == "Overview":
    st.subheader("Composite Livability Score")

    col_leg1, col_leg2, col_leg3, col_leg4 = st.columns(4)
    col_leg1.markdown("<span style='color:#4ade80'>A (70–100)</span>", unsafe_allow_html=True)
    col_leg2.markdown("<span style='color:#22c55e'>B (50–70)</span>", unsafe_allow_html=True)
    col_leg3.markdown("<span style='color:#f59e0b'>C (35–50)</span>", unsafe_allow_html=True)
    col_leg4.markdown("<span style='color:#ef4444'>D (&lt;35)</span>", unsafe_allow_html=True)

    df_s = df.sort_values("Composite_Score", ascending=True)
    fig_bar = go.Figure(go.Bar(
        x=df_s["Composite_Score"],
        y=df_s["Label"],
        orientation="h",
        marker=dict(color=df_s["Grade_Color"], line=dict(width=0)),
        text=df_s["Composite_Score"].apply(lambda x: f"{x:.1f}"),
        textposition="outside",
        textfont=dict(color="#7a8a72", size=9),
        hovertemplate="<b>%{y}</b><br>Score: %{x:.1f}<extra></extra>"
    ))
    fig_bar.update_layout(
        **PLOTLY_BASE,
        height=max(700, len(df) * 14),
        xaxis=dict(range=[0,112], showgrid=True, gridcolor="#2a3025",
                   title="Composite Score (0–100)", titlefont=dict(color="#7a8a72")),
        yaxis=dict(showgrid=False, tickfont=dict(size=9, color="#7a8a72")),
        margin=dict(l=10, r=60, t=10, b=40)
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")
    st.subheader("Income vs. Commute Time")
    fig_sc = px.scatter(
        df, x="Median_Income", y="Mean_Commute",
        size="Population", color="Composite_Score",
        color_continuous_scale=["#E53935","#FDD835","#1B5E20"],
        range_color=[0,100],
        hover_name="Label",
        hover_data={"Median_Income":":$,.0f","Mean_Commute":True,
                    "Pct_Bachelors":True,"Grade":True,"Composite_Score":":.1f"},
        labels={"Median_Income":"Median Income ($)",
                "Mean_Commute":"Mean Commute (min)",
                "Composite_Score":"Score"}
    )
    fig_sc.update_traces(marker=dict(opacity=0.85, line=dict(width=0.5, color="white")))
    fig_sc.update_layout(
        **PLOTLY_BASE,
        height=460,
        xaxis=dict(showgrid=True, gridcolor="#2a3025",
                   tickprefix="$", tickformat=",.0f",
                   titlefont=dict(color="#7a8a72")),
        yaxis=dict(showgrid=True, gridcolor="#2a3025",
                   titlefont=dict(color="#7a8a72")),
        margin=dict(l=10, r=10, t=10, b=50)
    )
    st.plotly_chart(fig_sc, use_container_width=True)

# ═══════════════════════════════════════════════════════════════
# PAGE: MAP
# ═══════════════════════════════════════════════════════════════
elif page == "Map":
    st.subheader("Geographic Distribution")

    ind_option = st.selectbox("Colour by", options=[
        "Composite_Score","Income_Score","Education_Score",
        "HomeValue_Score","Commute_Score","Density_Score"
    ], format_func=lambda x: {
        "Composite_Score":"Overall Score","Income_Score":"Income",
        "Education_Score":"Education","HomeValue_Score":"Home Value",
        "Commute_Score":"Commute","Density_Score":"Density"
    }[x])

    if geojson is not None and merged_gdf is not None:
        fig_map = px.choropleth_mapbox(
            merged_gdf,
            geojson=geojson,
            locations="ZCTA_str",
            color=ind_option,
            color_continuous_scale="Greens",
            range_color=[0,100],
            mapbox_style="open-street-map",
            zoom=8,
            center={"lat":42.50,"lon":-71.40},
            opacity=0.75,
            hover_data={
                "ZCTA_str":True,"Town":True,
                "Composite_Score":":.1f",
                "Median_Income":True,"Mean_Commute":True,
                "Pct_Bachelors":True,"Grade":True
            },
            labels={ind_option:"Score (0–100)"}
        )
        fig_map.update_layout(
            height=620,
            margin=dict(l=0,r=0,t=0,b=0),
            coloraxis_colorbar=dict(
                title="Score (0–100)",
                tickfont=dict(color="#7a8a72")
            )
        )
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.warning("Shapefile not found. Place `cb_2020_us_zcta520_500k/` in the same folder as app.py and restart.")

# ═══════════════════════════════════════════════════════════════
# PAGE: COMPARE
# ═══════════════════════════════════════════════════════════════
elif page == "Compare":
    st.subheader("Compare ZCTAs")

    labels = df.sort_values("Composite_Score", ascending=False)["Label"].tolist()

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        z1 = st.selectbox("ZCTA 1", labels, index=0)
    with col_s2:
        z2 = st.selectbox("ZCTA 2", labels, index=1)

    d1 = df[df["Label"] == z1].iloc[0]
    d2 = df[df["Label"] == z2].iloc[0]

    col_a, col_b = st.columns(2)
    for col, d in [(col_a, d1), (col_b, d2)]:
        c = grade_color(d["Composite_Score"])
        col.markdown(f"""
        <div style="background:{c}18;border:1px solid {c}44;border-radius:10px;
                    padding:24px;text-align:center;margin-bottom:16px">
          <div style="font-family:monospace;font-size:11px;color:{c};opacity:.8;margin-bottom:6px">
            {d['Town']} · {d['ZCTA_str']}
          </div>
          <div style="font-size:52px;font-weight:700;color:{c};line-height:1;margin-bottom:6px">
            {d['Composite_Score']:.1f}
          </div>
          <div style="font-family:monospace;font-size:11px;color:{c};opacity:.65">
            Grade {d['Grade']} · Rank #{int(d['Rank'])} of {len(df)}
          </div>
        </div>""", unsafe_allow_html=True)

    # Radar
    c1_hex = grade_color(d1["Composite_Score"])
    c2_hex = grade_color(d2["Composite_Score"])
    fig_radar = go.Figure()
    for d, color in [(d1, c1_hex), (d2, c2_hex)]:
        vals = [d[c] for c in SCORE_COLS] + [d[SCORE_COLS[0]]]
        fig_radar.add_trace(go.Scatterpolar(
            r=vals, theta=SCORE_NAMES+[SCORE_NAMES[0]],
            fill="toself",
            fillcolor=hex_to_rgba(color),
            line=dict(color=color, width=2.5),
            name=d["Label"]
        ))
    fig_radar.update_layout(
        **PLOTLY_BASE,
        height=420,
        polar=dict(
            radialaxis=dict(visible=True, range=[0,100],
                           ticksuffix="%", gridcolor="#2a3025",
                           linecolor="#2a3025", tickfont=dict(color="#7a8a72",size=9)),
            angularaxis=dict(tickfont=dict(color="#a0b090",size=12)),
            bgcolor="rgba(0,0,0,0)"
        ),
        legend=dict(font=dict(color="#a0b090",size=11))
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    # Comparison table
    rows = [
        ("Overall Score",   "Composite_Score",  lambda v: f"{v:.1f}"),
        ("Income Score",    "Income_Score",      lambda v: f"{v:.1f}"),
        ("Education Score", "Education_Score",   lambda v: f"{v:.1f}"),
        ("Home Value Score","HomeValue_Score",   lambda v: f"{v:.1f}"),
        ("Commute Score",   "Commute_Score",     lambda v: f"{v:.1f}"),
        ("Density Score",   "Density_Score",     lambda v: f"{v:.1f}"),
        ("Median Income",   "Median_Income",     lambda v: f"${v:,.0f}"),
        ("Home Value",      "Median_Home_Value", lambda v: f"${v:,.0f}"),
        ("Mean Commute",    "Mean_Commute",      lambda v: f"{v} min"),
        ("Bach. Degree+",   "Pct_Bachelors",     lambda v: f"{v}%"),
        ("Population",      "Population",        lambda v: f"{v:,.0f}"),
    ]
    score_keys = {"Composite_Score","Income_Score","Education_Score",
                  "HomeValue_Score","Commute_Score","Density_Score"}
    table_data = {"Indicator":[], d1["Town"]:[], d2["Town"]:[]}
    for label, key, fmt in rows:
        table_data["Indicator"].append(label)
        table_data[d1["Town"]].append(fmt(d1[key]))
        table_data[d2["Town"]].append(fmt(d2[key]))
    st.dataframe(pd.DataFrame(table_data), use_container_width=True, hide_index=True)

# ═══════════════════════════════════════════════════════════════
# PAGE: INDICATORS
# ═══════════════════════════════════════════════════════════════
elif page == "Indicators":
    st.subheader("Indicators")

    ind = st.selectbox("Select indicator", options=[
        "Composite_Score","Income_Score","Education_Score",
        "HomeValue_Score","Commute_Score","Density_Score"
    ], format_func=lambda x: {
        "Composite_Score":"Overall Score",
        "Income_Score":   "Income",
        "Education_Score":"Education",
        "HomeValue_Score":"Home Value",
        "Commute_Score":  "Commute",
        "Density_Score":  "Density"
    }[x])

    df_i = df.sort_values(ind, ascending=True)
    fig_i = go.Figure(go.Bar(
        x=df_i[ind],
        y=df_i["Label"],
        orientation="h",
        marker=dict(color=df_i[ind].apply(grade_color), line=dict(width=0)),
        text=df_i[ind].apply(lambda x: f"{x:.1f}"),
        textposition="outside",
        textfont=dict(color="#7a8a72", size=9),
        hovertemplate="<b>%{y}</b><br>Score: %{x:.1f}<extra></extra>"
    ))
    fig_i.update_layout(
        **PLOTLY_BASE,
        height=max(700, len(df)*14),
        xaxis=dict(range=[0,115], showgrid=True, gridcolor="#2a3025",
                   title="Score (0–100)", titlefont=dict(color="#7a8a72")),
        yaxis=dict(showgrid=False, tickfont=dict(size=9, color="#7a8a72")),
        margin=dict(l=10, r=60, t=10, b=40)
    )
    st.plotly_chart(fig_i, use_container_width=True)

    # Radar for top 10
    st.markdown("---")
    st.subheader("Top 10 Profile")
    df_top10 = df.nlargest(10, "Composite_Score").reset_index(drop=True)
    fig_r = go.Figure()
    for i, (_, row) in enumerate(df_top10.iterrows()):
        fc, lc = PALETTE_RGBA[i]
        vals = [row[c] for c in SCORE_COLS] + [row[SCORE_COLS[0]]]
        fig_r.add_trace(go.Scatterpolar(
            r=vals, theta=SCORE_NAMES+[SCORE_NAMES[0]],
            fill="toself", fillcolor=fc,
            line=dict(color=lc, width=2),
            name=row["Label"]
        ))
    fig_r.update_layout(
        **PLOTLY_BASE,
        height=500,
        polar=dict(
            radialaxis=dict(visible=True, range=[0,100],
                           ticksuffix="%", gridcolor="#2a3025",
                           linecolor="#2a3025", tickfont=dict(color="#7a8a72",size=9)),
            angularaxis=dict(tickfont=dict(color="#a0b090",size=12)),
            bgcolor="rgba(0,0,0,0)"
        ),
        legend=dict(font=dict(color="#a0b090",size=10), x=1.05, y=1.0)
    )
    st.plotly_chart(fig_r, use_container_width=True)

# ═══════════════════════════════════════════════════════════════
# PAGE: DATA
# ═══════════════════════════════════════════════════════════════
elif page == "Data":
    st.subheader("Full Dataset")
    

    cols = ["Rank","Town","ZCTA_str","Grade","Composite_Score",
            "Median_Income","Median_Home_Value","Mean_Commute",
            "Pct_Bachelors","Population",
            "Income_Score","Education_Score","HomeValue_Score",
            "Commute_Score","Density_Score"]
    disp = df.sort_values("Rank")[cols].copy()
    disp.columns = ["Rank","Town","ZCTA","Grade","Score",
                    "Income ($)","Home Value ($)","Commute (min)",
                    "Bach.+ (%)","Population",
                    "Income Score","Edu Score","Home Score",
                    "Commute Score","Density Score"]
    st.dataframe(disp, use_container_width=True, hide_index=True)

    csv = disp.to_csv(index=False)
    st.download_button(
        "Download CSV",
        data=csv,
        file_name="middlesex_zcta_livability.csv",
        mime="text/csv"
    )
