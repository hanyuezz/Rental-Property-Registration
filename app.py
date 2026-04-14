import streamlit as st
import pandas as pd
import plotly.express as px

# ----------------------------
# Page setup
# ----------------------------
st.set_page_config(page_title="Seattle Rental Dashboard", layout="wide")

st.title("Seattle Rental Property Dashboard")

st.markdown("""
This dashboard explores rental property patterns in Seattle, focusing on location, size distribution, and trends over time.
""")

# ----------------------------
# Load data
# ----------------------------
df = pd.read_csv("Rental_Property_Registration_20260413.csv")

# Cleaning
df["RegisteredDate"] = pd.to_datetime(df["RegisteredDate"], errors="coerce")
df["RentalHousingUnits"] = pd.to_numeric(df["RentalHousingUnits"], errors="coerce")
df["Latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")
df["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")
df["OriginalZip"] = pd.to_numeric(df["OriginalZip"], errors="coerce")

df = df.dropna(subset=["RegisteredDate", "RentalHousingUnits", "Latitude", "Longitude", "OriginalZip"])

df["OriginalZip"] = df["OriginalZip"].astype(int).astype(str)

# ----------------------------
# Feature Engineering
# ----------------------------
def categorize_units(x):
    if x <= 5:
        return "Small"
    elif x <= 20:
        return "Medium"
    else:
        return "Large"

df["UnitCategory"] = df["RentalHousingUnits"].apply(categorize_units)
df["Year"] = df["RegisteredDate"].dt.year

# ----------------------------
# Sidebar Filters
# ----------------------------
st.sidebar.header("Filters")

# Unit range
max_units = int(df["RentalHousingUnits"].max())
unit_range = st.sidebar.slider("Units Range", 0, max_units, (0, 20))

# Zip filter
zip_options = sorted(df["OriginalZip"].unique())
selected_zips = st.sidebar.multiselect("Select Zip Codes", zip_options, default=zip_options)

# Category filter
category_options = ["Small", "Medium", "Large"]
selected_categories = st.sidebar.multiselect("Unit Category", category_options, default=category_options)

# Apply filters
df_filtered = df[
    (df["RentalHousingUnits"] >= unit_range[0]) &
    (df["RentalHousingUnits"] <= unit_range[1]) &
    (df["OriginalZip"].isin(selected_zips)) &
    (df["UnitCategory"].isin(selected_categories))
]

# ----------------------------
# Layout
# ----------------------------
col1, col2 = st.columns(2)

# ----------------------------
# Chart 1: Density Map
# ----------------------------
with col1:
    st.subheader("Density Map")

    fig_map = px.density_mapbox(
        df_filtered,
        lat="Latitude",
        lon="Longitude",
        z="RentalHousingUnits",
        radius=10,
        center=dict(lat=47.6062, lon=-122.3321),
        zoom=10,
        mapbox_style="carto-positron"
    )
    st.plotly_chart(fig_map, use_container_width=True)

# ----------------------------
# Chart 2: Histogram
# ----------------------------
with col2:
    st.subheader("Unit Distribution")

    fig_hist = px.histogram(
        df_filtered[df_filtered["RentalHousingUnits"] <= 20],
        x="RentalHousingUnits",
        nbins=20
    )
    st.plotly_chart(fig_hist, use_container_width=True)

# ----------------------------
# Chart 3: Zip Code Bar
# ----------------------------
col3, col4 = st.columns(2)

with col3:
    st.subheader("Top Zip Codes")

    zip_count = df_filtered["OriginalZip"].value_counts().nlargest(10).reset_index()
    zip_count.columns = ["zip", "count"]

    fig_zip = px.bar(zip_count, x="zip", y="count")
    st.plotly_chart(fig_zip, use_container_width=True)

# ----------------------------
# Chart 4: Time Trend
# ----------------------------
with col4:
    st.subheader("Registration Trend")

    monthly = (
        df_filtered
        .groupby(df_filtered["RegisteredDate"].dt.to_period("M"))
        .size()
        .reset_index(name="count")
    )

    monthly["RegisteredDate"] = pd.to_datetime(monthly["RegisteredDate"].astype(str))

    fig_time = px.area(monthly, x="RegisteredDate", y="count")
    st.plotly_chart(fig_time, use_container_width=True)

# ----------------------------
# Extra Chart: Category Distribution
# ----------------------------
st.subheader("Property Size Categories")

cat_count = df_filtered["UnitCategory"].value_counts().reset_index()
cat_count.columns = ["Category", "count"]

fig_cat = px.pie(cat_count, names="Category", values="count")
st.plotly_chart(fig_cat, use_container_width=True)
