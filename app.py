import streamlit as st
import pandas as pd
import plotly.express as px

# ----------------------------
# Page config
# ----------------------------
st.set_page_config(
    page_title="Seattle Rental Property Dashboard",
    layout="wide"
)

# ----------------------------
# Title and overview
# ----------------------------
st.title("Seattle Rental Property Dashboard")

st.markdown("""
This dashboard explores rental property patterns in Seattle.
It focuses on spatial distribution, property size, differences across zip codes, and registration trends over time.
""")

# ----------------------------
# Load data
# ----------------------------
df = pd.read_csv("Rental_Property_Registration_20260413.csv")

# Data cleaning
df["RegisteredDate"] = pd.to_datetime(df["RegisteredDate"], errors="coerce")
df["RentalHousingUnits"] = pd.to_numeric(df["RentalHousingUnits"], errors="coerce")
df["Latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")
df["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")
df["OriginalZip"] = pd.to_numeric(df["OriginalZip"], errors="coerce")

df = df.dropna(subset=["RegisteredDate", "RentalHousingUnits", "Latitude", "Longitude", "OriginalZip"])
df["OriginalZip"] = df["OriginalZip"].astype(int).astype(str)

# ----------------------------
# Sidebar filters
# ----------------------------
st.sidebar.header("Filters")

max_units = int(df["RentalHousingUnits"].max())
unit_range = st.sidebar.slider(
    "Select rental unit range",
    min_value=0,
    max_value=max_units,
    value=(0, min(20, max_units))
)

top_zip_options = sorted(df["OriginalZip"].unique().tolist())
selected_zips = st.sidebar.multiselect(
    "Select zip codes",
    options=top_zip_options,
    default=top_zip_options
)

# Apply filters
df_filtered = df[
    (df["RentalHousingUnits"] >= unit_range[0]) &
    (df["RentalHousingUnits"] <= unit_range[1]) &
    (df["OriginalZip"].isin(selected_zips))
]

# ----------------------------
# Chart 1: Density Map
# ----------------------------
st.subheader("1. Density of Rental Properties")

fig_map = px.density_mapbox(
    df_filtered,
    lat="Latitude",
    lon="Longitude",
    z="RentalHousingUnits",
    radius=10,
    center=dict(lat=47.6062, lon=-122.3321),
    zoom=10,
    mapbox_style="carto-positron",
    title="Density of Rental Properties"
)
st.plotly_chart(fig_map, use_container_width=True)

st.caption("Rental properties are concentrated in certain areas, especially in central Seattle.")

# ----------------------------
# Chart 2: Histogram
# ----------------------------
st.subheader("2. Distribution of Rental Housing Units")

fig_hist = px.histogram(
    df_filtered[df_filtered["RentalHousingUnits"] <= 20],
    x="RentalHousingUnits",
    nbins=20,
    title="Distribution of Rental Housing Units (0–20 Range)"
)
st.plotly_chart(fig_hist, use_container_width=True)

st.caption("Most properties have a small number of units, while larger properties are less common.")

# ----------------------------
# Chart 3: Zip Code Bar
# ----------------------------
st.subheader("3. Top Zip Codes by Number of Properties")

zip_count = (
    df_filtered["OriginalZip"]
    .value_counts()
    .nlargest(10)
    .reset_index()
)
zip_count.columns = ["zip", "count"]

fig_zip = px.bar(
    zip_count,
    x="zip",
    y="count",
    title="Top 10 Zip Codes by Number of Properties"
)
st.plotly_chart(fig_zip, use_container_width=True)

st.caption("Some zip codes have noticeably more registered rental properties than others.")

# ----------------------------
# Chart 4: Time Trend
# ----------------------------
st.subheader("4. Registration Trend Over Time")

monthly = (
    df_filtered
    .groupby(df_filtered["RegisteredDate"].dt.to_period("M"))
    .size()
    .reset_index(name="count")
)
monthly["RegisteredDate"] = monthly["RegisteredDate"].astype(str)
monthly["RegisteredDate"] = pd.to_datetime(monthly["RegisteredDate"])

fig_time = px.area(
    monthly,
    x="RegisteredDate",
    y="count",
    title="Rental Property Registrations Over Time"
)
st.plotly_chart(fig_time, use_container_width=True)

st.caption("Registration activity changes over time and shows an overall upward trend in the dataset.")
