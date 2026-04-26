import os
import zipfile
import urllib.request
import warnings
import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.graph_objects as go
warnings.filterwarnings("ignore")

st.set_page_config(page_title="USPTO Patent Activity", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
[data-testid="stAppViewContainer"]{background:#FAFAF7}
[data-testid="stSidebar"]{display:none}
[data-testid="collapsedControl"]{display:none}
header[data-testid="stHeader"]{background:transparent}
.block-container{padding:0!important;max-width:100%!important}
h1,h2,h3{color:#1A1612!important}
footer{visibility:hidden}
.stMetric{background:white!important;border:1px solid #DDD8CE!important;border-top:3px solid #0F2557!important;border-radius:0 0 4px 4px!important;padding:16px!important}
.stMetric label{color:#7A7268!important;font-size:10px!important;letter-spacing:1px!important;text-transform:uppercase!important;font-family:monospace!important}
.stMetric [data-testid="stMetricValue"]{color:#0F2557!important;font-size:22px!important;font-weight:700!important}
.stRadio label{color:#7A7268!important;font-size:13px!important}
.stDownloadButton button{background:#0F2557!important;color:white!important;border:none!important}
</style>
""", unsafe_allow_html=True)

POP_2015 = {
    "AK":738432,"AL":4858979,"AR":2978204,"AZ":6828065,"CA":39144818,
    "CO":5456574,"CT":3590886,"DC":672228,"DE":945934,"FL":20271272,
    "GA":10214860,"HI":1431603,"IA":3123899,"ID":1654930,"IL":12859995,
    "IN":6619680,"KS":2911641,"KY":4425092,"LA":4670724,"MA":6794422,
    "MD":6006401,"ME":1329328,"MI":9922576,"MN":5489594,"MO":6083672,
    "MS":2992333,"MT":1032949,"NC":10042802,"ND":756927,"NE":1896190,
    "NH":1330608,"NJ":8958013,"NM":2085109,"NV":2890845,"NY":19795791,
    "OH":11613423,"OK":3911338,"OR":4028977,"PA":12802503,"RI":1056298,
    "SC":4896146,"SD":858469,"TN":6600299,"TX":27469114,"UT":2995919,
    "VA":8382993,"VT":626042,"WA":7170351,"WI":5771337,"WV":1844128,"WY":586107,
}

METROS = [
    ("San Jose-Sunnyvale-Santa Clara, CA", 14618),
    ("San Francisco-Oakland-Fremont, CA", 9732),
    ("New York-N. New Jersey-Long Island, NY-NJ-PA", 7754),
    ("Los Angeles-Long Beach-Santa Ana, CA", 6476),
    ("Boston-Cambridge-Quincy, MA-NH", 5949),
    ("San Diego-Carlsbad-San Marcos, CA", 5460),
    ("Seattle-Tacoma-Bellevue, WA", 4739),
    ("Chicago-Joliet-Naperville, IL-IN-WI", 3909),
    ("Minneapolis-St. Paul-Bloomington, MN-WI", 3419),
    ("Detroit-Warren-Livonia, MI", 3305),
    ("Houston-Sugar Land-Baytown, TX", 3186),
    ("Dallas-Fort Worth-Arlington, TX", 3026),
    ("Austin-Round Rock-San Marcos, TX", 2700),
    ("Philadelphia-Camden-Wilmington, PA-NJ-DE-MD", 2357),
    ("Portland-Vancouver-Hillsboro, OR-WA", 2163),
]

def navy_scale(vals):
    mx,q7,q4 = vals.max(),vals.quantile(.7),vals.quantile(.4)
    return ["#C8870A" if v==mx else "#0F2557" if v>=q7 else "#1A3A8C" if v>=q4 else "#7DB3E8" for v in vals]

def green_scale(vals):
    mx,q7,q4 = vals.max(),vals.quantile(.7),vals.quantile(.4)
    return ["#C8870A" if v==mx else "#276749" if v>=q7 else "#48BB78" if v>=q4 else "#9AE6B4" for v in vals]

def apply_style(fig, height=500):
    fig.layout.paper_bgcolor = "rgba(0,0,0,0)"
    fig.layout.plot_bgcolor  = "rgba(0,0,0,0)"
    fig.layout.height        = height
    fig.layout.font          = dict(family="sans-serif", color="#7A7268", size=12)
    return fig

@st.cache_data
def load_data():
    df = pd.read_csv("uspto_patent_map/Patents.csv", encoding="latin1")
    df = df.dropna(subset=["Patents_2015"])
    def state_from_msa(name):
        parts = str(name).split(",")
        if len(parts) > 1:
            p = parts[-1].strip().split("-")[0].strip()
            if len(p)==2 and p.isalpha():
                return p.upper()
        return None
    df["State"] = df["MSA_Name"].apply(state_from_msa)
    df_c = df[df["State"].notna()].copy()
    sp = df_c.groupby("State")["Patents_2015"].sum().reset_index().rename(columns={"Patents_2015":"Patents"})
    sp["Patents"]    = sp["Patents"].astype(int)
    sp["Population"] = sp["State"].map(POP_2015)
    sp = sp.dropna(subset=["Population"])
    sp["Population"] = sp["Population"].astype(int)
    sp["PerCapita"]  = ((sp["Patents"]/sp["Population"])*100_000).round(1)
    return sp

@st.cache_data
def load_geo(_sp):
    shp_path = "tl_2020_us_state/tl_2020_us_state.shp"
    if not os.path.exists(shp_path):
        with st.spinner("Downloading state boundaries..."):
            urllib.request.urlretrieve(
                "https://www2.census.gov/geo/tiger/TIGER2020/STATE/tl_2020_us_state.zip",
                "tl_2020_us_state.zip"
            )
            with zipfile.ZipFile("tl_2020_us_state.zip","r") as z:
                z.extractall("tl_2020_us_state")
            os.remove("tl_2020_us_state.zip")
    try:
        gdf = gpd.read_file(shp_path)
        gdf = gdf.to_crs(epsg=4326)
        gdf = gdf[~gdf["STUSPS"].isin(["PR","VI","GU","MP","AS"])].copy()
        mg  = gdf.merge(_sp, left_on="STUSPS", right_on="State", how="left")
        mg["Patents"]    = mg["Patents"].fillna(0).astype(int)
        mg["PerCapita"]  = mg["PerCapita"].fillna(0.0)
        mg["Population"] = mg["Population"].fillna(0).astype(int)
        return mg
    except Exception:
        return None

sp = load_data()
mg = load_geo(sp)
top_raw = sp.nlargest(1,"Patents").iloc[0]
top_pc  = sp.nlargest(1,"PerCapita").iloc[0]

st.markdown("""
<div style="background:#0F2557;padding:14px 64px;display:flex;align-items:center;justify-content:space-between;border-bottom:3px solid #C8870A">
  <div style="font-family:Georgia,serif;font-size:16px;color:white;font-weight:700">USPTO Patent Activity — 2015</div>
  <div style="font-family:monospace;font-size:10px;color:rgba(255,255,255,.4);letter-spacing:2px;text-transform:uppercase">Hetvi Chavda · Northeastern University</div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div style="background:#0F2557;padding:80px 64px 72px;position:relative">
  <div style="position:absolute;bottom:0;left:0;right:0;height:4px;background:linear-gradient(90deg,#C8870A,#F0A820,#2D5BE3)"></div>
  <p style="font-family:monospace;font-size:10px;letter-spacing:3px;text-transform:uppercase;color:#C8870A;margin-bottom:18px">USPTO · Utility Patent Grants · 2015</p>
  <h1 style="font-family:Georgia,serif;font-size:48px;line-height:1.05;color:white;margin-bottom:20px;font-weight:700;max-width:700px">USPTO Patent Activity<br><span style="color:#C8870A">U.S. State Analysis</span></h1>
  <p style="font-size:15px;color:rgba(255,255,255,.55);max-width:560px;line-height:1.75;margin-bottom:40px">Utility patent grants mapped across all 50 states — raw count and per-capita. Built with GeoPandas, Matplotlib, and Plotly on Census TIGER/Line boundaries.</p>
  <div style="display:flex;gap:48px;flex-wrap:wrap">
    <div style="border-left:2px solid #C8870A;padding-left:16px">
      <div style="font-family:Georgia,serif;font-size:32px;color:#C8870A;line-height:1">{sp["Patents"].sum():,}</div>
      <div style="font-family:monospace;font-size:10px;color:rgba(255,255,255,.4);text-transform:uppercase;letter-spacing:1px;margin-top:4px">Patents Mapped</div>
    </div>
    <div style="border-left:2px solid #C8870A;padding-left:16px">
      <div style="font-family:Georgia,serif;font-size:32px;color:#C8870A;line-height:1">51</div>
      <div style="font-family:monospace;font-size:10px;color:rgba(255,255,255,.4);text-transform:uppercase;letter-spacing:1px;margin-top:4px">States + DC</div>
    </div>
    <div style="border-left:2px solid #C8870A;padding-left:16px">
      <div style="font-family:Georgia,serif;font-size:32px;color:#C8870A;line-height:1">{top_raw["State"]}</div>
      <div style="font-family:monospace;font-size:10px;color:rgba(255,255,255,.4);text-transform:uppercase;letter-spacing:1px;margin-top:4px">Leads Raw Count</div>
    </div>
    <div style="border-left:2px solid #C8870A;padding-left:16px">
      <div style="font-family:Georgia,serif;font-size:32px;color:#C8870A;line-height:1">{top_pc["State"]}</div>
      <div style="font-family:monospace;font-size:10px;color:rgba(255,255,255,.4);text-transform:uppercase;letter-spacing:1px;margin-top:4px">Leads Per Capita</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# CHOROPLETH
st.markdown("""
<div style="padding:48px 64px 0;border-top:1px solid #DDD8CE">
  <p style="font-family:monospace;font-size:10px;letter-spacing:3px;text-transform:uppercase;color:#C8870A;margin-bottom:10px">Choropleth</p>
  <h2 style="font-family:Georgia,serif;font-size:30px;color:#1A1612;margin-bottom:24px;font-weight:700">Patent Grants by State</h2>
</div>
""", unsafe_allow_html=True)

mode = st.radio("", ["Raw Patent Count","Per 100,000 People"], horizontal=True, label_visibility="collapsed", key="map_mode")
is_pc = mode == "Per 100,000 People"
z = "PerCapita" if is_pc else "Patents"
cs = ([[0,"#F0FFF4"],[0.15,"#C6F6D5"],[0.3,"#9AE6B4"],[0.5,"#48BB78"],[0.7,"#276749"],[0.85,"#1C4532"],[1,"#0A2818"]]
      if is_pc else
      [[0,"#EBF5FF"],[0.15,"#90CDF4"],[0.35,"#4299E1"],[0.6,"#2B6CB0"],[0.8,"#1A365D"],[1,"#0A1628"]])

if mg is not None:
    hover = mg.apply(lambda r:
        f"<b>{r['NAME']} ({r['STUSPS']})</b><br>Patents: {r['Patents']:,}<br>Per 100K: {r['PerCapita']}<br>Population: {r['Population']:,}"
        if r["Patents"]>0 else f"<b>{r['NAME']}</b><br>No data", axis=1)
    fig = go.Figure(go.Choropleth(
        locationmode="USA-states", locations=mg["STUSPS"], z=mg[z],
        text=hover, hoverinfo="text", colorscale=cs,
        colorbar=dict(title=dict(text="Per 100K" if is_pc else "Patents", font=dict(size=11,color="#7A7268")),
                      tickfont=dict(size=10,color="#7A7268"), bgcolor="rgba(0,0,0,0)", bordercolor="#DDD8CE", borderwidth=1),
        marker=dict(line=dict(color="#FAFAF7",width=1.5))
    ))
    fig = apply_style(fig, 480)
    fig.update_layout(geo=dict(scope="usa", showland=True, landcolor="#D4D0C8",
                          showocean=True, oceancolor="#B8D4E8",
                          showcoastlines=True, coastlinecolor="#8A8580",
                          showframe=False, bgcolor="rgba(0,0,0,0)",
                          subunitcolor="#8A8580", lakecolor="#B8D4E8"))
    fig.update_layout(margin=dict(l=0,r=0,t=10,b=0))
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Map loading — shapefile downloading on first run.")

col1,col2 = st.columns(2)
with col1:
    st.markdown("""<div style="border-left:4px solid #C8870A;padding:18px 24px;background:white;border-radius:0 4px 4px 0;margin-top:8px">
      <div style="font-family:Georgia,serif;font-size:44px;color:#C8870A;font-weight:700;line-height:1;margin-bottom:8px">40,134</div>
      <div style="font-size:13px;color:#7A7268;line-height:1.6">California patents in 2015. Nearly 4x the next state. Raw counts heavily favour large-population states.</div>
    </div>""", unsafe_allow_html=True)
with col2:
    st.markdown("""<div style="border-left:4px solid #0F2557;padding:18px 24px;background:white;border-radius:0 4px 4px 0;margin-top:8px">
      <div style="font-family:Georgia,serif;font-size:44px;color:#0F2557;font-weight:700;line-height:1;margin-bottom:8px">343.6</div>
      <div style="font-size:13px;color:#7A7268;line-height:1.6">DC patents per 100,000 people. #1 per capita. Federal research institutions in a very small geography.</div>
    </div>""", unsafe_allow_html=True)

# RANKINGS
st.markdown("""
<div style="padding:48px 64px 0;border-top:1px solid #DDD8CE;margin-top:20px;background:white">
  <p style="font-family:monospace;font-size:10px;letter-spacing:3px;text-transform:uppercase;color:#C8870A;margin-bottom:10px">Rankings</p>
  <h2 style="font-family:Georgia,serif;font-size:30px;color:#1A1612;margin-bottom:24px;font-weight:700">Raw Count vs. Per Capita</h2>
</div>
""", unsafe_allow_html=True)

top_raw_25 = sp.nlargest(25,"Patents").sort_values("Patents",ascending=True)
top_pc_25  = sp.nlargest(25,"PerCapita").sort_values("PerCapita",ascending=True)

col1,col2 = st.columns(2)
with col1:
    fig1 = go.Figure(go.Bar(
        x=top_raw_25["Patents"], y=top_raw_25["State"], orientation="h",
        marker=dict(color=navy_scale(top_raw_25["Patents"]),line=dict(width=0)),
        text=top_raw_25["Patents"].apply(lambda x: f"{x:,}"), textposition="outside",
        textfont=dict(color="#7A7268",size=10),
        hovertemplate="<b>%{y}</b><br>Patents: %{x:,}<extra></extra>"
    ))
    fig1 = apply_style(fig1, 540)
    fig1.update_layout(title_text="Raw Count")
    fig1.update_xaxes(showgrid=True, gridcolor="#E8E3DA", zerolinecolor="#C8C2B6", tickformat=",")
    fig1.update_yaxes(showgrid=False, tickfont=dict(size=11,color="#3D3530"))
    fig1.update_layout(margin=dict(l=40,r=80,t=40,b=40))
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    fig2 = go.Figure(go.Bar(
        x=top_pc_25["PerCapita"], y=top_pc_25["State"], orientation="h",
        marker=dict(color=green_scale(top_pc_25["PerCapita"]),line=dict(width=0)),
        text=top_pc_25["PerCapita"].apply(lambda x: f"{x:.1f}"), textposition="outside",
        textfont=dict(color="#7A7268",size=10),
        hovertemplate="<b>%{y}</b><br>Per 100K: %{x:.1f}<extra></extra>"
    ))
    fig2 = apply_style(fig2, 540)
    fig2.update_layout(title_text="Per 100,000 People")
    fig2.update_xaxes(showgrid=True, gridcolor="#E8E3DA", zerolinecolor="#C8C2B6")
    fig2.update_yaxes(showgrid=False, tickfont=dict(size=11,color="#3D3530"))
    fig2.update_layout(margin=dict(l=40,r=60,t=40,b=40))
    st.plotly_chart(fig2, use_container_width=True)

# METRO AREAS
st.markdown("""
<div style="padding:48px 64px 0;border-top:1px solid #DDD8CE">
  <p style="font-family:monospace;font-size:10px;letter-spacing:3px;text-transform:uppercase;color:#C8870A;margin-bottom:10px">Metro Areas</p>
  <h2 style="font-family:Georgia,serif;font-size:30px;color:#1A1612;margin-bottom:24px;font-weight:700">Top 15 Metro Areas</h2>
</div>
""", unsafe_allow_html=True)

c1,c2,c3,c4 = st.columns(4)
c1.metric("San Jose","14,618","#1 Silicon Valley")
c2.metric("San Francisco","9,732","#2 Bay Area")
c3.metric("Boston-Cambridge","5,949","#5 Route 128")
c4.metric("Minneapolis","3,419","#9 Med Devices")

mdf = pd.DataFrame(METROS, columns=["Metro","Patents"])
mdf["Short"] = mdf["Metro"].apply(lambda x: x.split(",")[0])
ms = mdf.sort_values("Patents",ascending=True)
fig_m = go.Figure(go.Bar(
    x=ms["Patents"], y=ms["Short"], orientation="h",
    marker=dict(color=navy_scale(ms["Patents"]),line=dict(width=0)),
    text=ms["Patents"].apply(lambda x: f"{x:,}"), textposition="outside",
    textfont=dict(color="#7A7268",size=11),
    customdata=ms["Metro"],
    hovertemplate="<b>%{customdata}</b><br>Patents: %{x:,}<extra></extra>"
))
fig_m = apply_style(fig_m, 480)
fig_m.update_xaxes(showgrid=True, gridcolor="#E8E3DA", zerolinecolor="#C8C2B6",
                   tickformat=",", title="Patent Grants 2015")
fig_m.update_yaxes(showgrid=False, tickfont=dict(size=11,color="#3D3530"))
fig_m.update_layout(margin=dict(l=10,r=90,t=10,b=50))
st.plotly_chart(fig_m, use_container_width=True)

# KEY NUMBERS
st.markdown("""
<div style="padding:48px 64px;border-top:1px solid #DDD8CE;background:white">
  <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:1px;background:#DDD8CE;border:1px solid #DDD8CE;border-radius:4px;overflow:hidden">
    <div style="background:white;padding:32px">
      <div style="font-family:Georgia,serif;font-size:56px;font-weight:700;color:#C8870A;line-height:1;margin-bottom:10px">4x</div>
      <div style="font-family:monospace;font-size:10px;color:#0F2557;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px">California vs. Next State</div>
      <p style="font-size:12px;color:#7A7268;line-height:1.6;margin:0">CA produced 40,134 patents — nearly four times New York's 12,244. No other state comes close in raw volume.</p>
    </div>
    <div style="background:white;padding:32px">
      <div style="font-family:Georgia,serif;font-size:56px;font-weight:700;color:#0F2557;line-height:1;margin-bottom:10px">#1</div>
      <div style="font-family:monospace;font-size:10px;color:#0F2557;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px">DC Per Capita</div>
      <p style="font-size:12px;color:#7A7268;line-height:1.6;margin:0">343.6 patents per 100,000 people. DC has 672K residents and 2,310 patents — the most innovation-dense geography in the country.</p>
    </div>
    <div style="background:white;padding:32px">
      <div style="font-family:Georgia,serif;font-size:56px;font-weight:700;color:#276749;line-height:1;margin-bottom:10px">5th</div>
      <div style="font-family:monospace;font-size:10px;color:#0F2557;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px">Boston Nationally</div>
      <p style="font-size:12px;color:#7A7268;line-height:1.6;margin:0">Boston-Cambridge ranks 5th among all U.S. metros at 5,949 grants. Massachusetts ranks top-3 per capita at 100.8.</p>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# DATA
st.markdown("""
<div style="padding:48px 64px 0;border-top:1px solid #DDD8CE">
  <p style="font-family:monospace;font-size:10px;letter-spacing:3px;text-transform:uppercase;color:#C8870A;margin-bottom:10px">Data</p>
  <h2 style="font-family:Georgia,serif;font-size:30px;color:#1A1612;margin-bottom:24px;font-weight:700">Full Dataset</h2>
</div>
""", unsafe_allow_html=True)

by_raw = sp.sort_values("Patents",ascending=False).reset_index(drop=True)
pc_rank = {r["State"]:i+1 for i,r in sp.sort_values("PerCapita",ascending=False).reset_index(drop=True).iterrows()}
by_raw["Raw Rank"]        = by_raw.index+1
by_raw["Per Capita Rank"] = by_raw["State"].map(pc_rank)
disp = by_raw[["Raw Rank","State","Patents","Population","PerCapita","Per Capita Rank"]].copy()
disp.columns = ["Raw Rank","State","Patents","Population","Per 100K","Per Capita Rank"]
disp["Patents"]    = disp["Patents"].apply(lambda x: f"{x:,}")
disp["Population"] = disp["Population"].apply(lambda x: f"{x:,}")
st.dataframe(disp, use_container_width=True, hide_index=True)
st.download_button("Download CSV", data=sp.to_csv(index=False), file_name="uspto_patent_state_data.csv", mime="text/csv")

st.markdown("""
<div style="background:#0F2557;border-top:3px solid #C8870A;padding:24px 64px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;margin-top:20px">
  <div style="font-family:monospace;font-size:11px;color:rgba(255,255,255,.5)"><strong style="color:#C8870A">Hetvi Chavda</strong></div>
  <div style="font-family:monospace;font-size:10px;color:rgba(255,255,255,.3)">USPTO 2015 · Census TIGER/Line · Python · GeoPandas · Plotly</div>
</div>
""", unsafe_allow_html=True)
