import streamlit as st
import pandas as pd
import plotly.express as px

# ----------------------------
# Page setup
# ----------------------------
st.set_page_config(
    page_title="Seattle Rental Property Dashboard",
    layout="wide"
)

# ----------------------------
# Title and intro
# ----------------------------
st.title("Seattle Rental Property Dashboard")
st.markdown(
    """
    This dashboard explores rental property patterns in Seattle, focusing on location,
    unit distribution, area differences, and registration activity over time.
    """
)

# ----------------------------
# Load data
# ----------------------------
df = pd.read_csv("Rental_Property_Registration_20260413.csv")

# ----------------------------
# Data cleaning
# ----------------------------
df["RegisteredDate"] = pd.to_datetime(df["RegisteredDate"], errors="coerce")
df["RentalHousingUnits"] = pd.to_numeric(df["RentalHousingUnits"], errors="coerce")
df["Latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")
df["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")

# clean zip to 5-digit string
df["OriginalZip"] = (
    df["OriginalZip"]
    .astype(str)
    .str.extract(r"(\d{5})")[0]
)

df = df.dropna(
    subset=["RegisteredDate", "RentalHousingUnits", "Latitude", "Longitude", "OriginalZip"]
).copy()

# ----------------------------
# Fix obvious zip typos found in file
# ----------------------------
df["OriginalZip"] = df["OriginalZip"].replace({
    "89133": "98133",
    "90105": "98105"
})

# ----------------------------
# ZIP to area mapping
# ----------------------------
zip_area_map = {
    "98101": "Downtown",
    "98102": "Capitol Hill / Eastlake",
    "98103": "Green Lake / North Seattle",
    "98104": "Downtown / International District",
    "98105": "University District / Laurelhurst",
    "98106": "Delridge",
    "98107": "Ballard",
    "98108": "South Park / Georgetown",
    "98109": "Queen Anne / South Lake Union",
    "98112": "Central Area / Madison Park",
    "98115": "Northeast Seattle",
    "98116": "West Seattle",
    "98117": "Northwest Seattle",
    "98118": "Rainier Valley",
    "98119": "Queen Anne / Magnolia",
    "98121": "Belltown",
    "98122": "Central District / Capitol Hill",
    "98125": "Lake City / North Seattle",
    "98126": "West Seattle / Delridge",
    "98133": "North Seattle / Bitter Lake",
    "98134": "SoDo / Industrial Area",
    "98136": "West Seattle / Fauntleroy",
    "98144": "Beacon Hill / Mount Baker",
    "98146": "Southwest Seattle",
    "98155": "North Seattle Border Area",
    "98164": "Downtown / Financial District",
    "98168": "South Seattle Border Area",
    "98177": "Northwest Seattle / Crown Hill",
    "98178": "South Seattle Border Area",
    "98199": "Magnolia"
}

# only keep zips that appear in your file, and make sure all of them get a name
file_zips = sorted(df["OriginalZip"].unique().tolist())
for z in file_zips:
    if z not in zip_area_map:
        zip_area_map[z] = f"Seattle Area {z}"

df["AreaName"] = df["OriginalZip"].map(zip_area_map)

# helper label
df["ZipAreaLabel"] = df["OriginalZip"] + " - " + df["AreaName"]

# ----------------------------
# Feature engineering
# ----------------------------
def categorize_units(x):
    if x <= 5:
        return "Small"
    elif x <= 20:
        return "Medium"
    else:
        return "Large"

df["UnitCategory"] = df["RentalHousingUnits"].apply(categorize_units)

# ----------------------------
# Sidebar filters
# ----------------------------
st.sidebar.header("Filters")

# Units filter
max_units = int(df["RentalHousingUnits"].max())
unit_range = st.sidebar.slider(
    "Units Range",
    min_value=0,
    max_value=max_units,
    value=(0, max_units)
)

# Date range filter
st.sidebar.subheader("Time Filter")
min_date = df["RegisteredDate"].min().date()
max_date = df["RegisteredDate"].max().date()

date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date = min_date
    end_date = max_date

# Zip filter
zip_options = sorted(df["OriginalZip"].unique().tolist())
selected_zips = st.sidebar.multiselect(
    "Select Zip Codes",
    options=zip_options,
    default=zip_options
)

# Category filter
category_options = ["Small", "Medium", "Large"]
selected_categories = st.sidebar.multiselect(
    "Unit Category",
    options=category_options,
    default=category_options
)

st.sidebar.caption(
    "Property categories: Small = 1–5 units, Medium = 6–20 units, Large = 21+ units"
)

# ----------------------------
# Filtered dataset
# ----------------------------
df_filtered = df[
    (df["RentalHousingUnits"] >= unit_range[0]) &
    (df["RentalHousingUnits"] <= unit_range[1]) &
    (df["OriginalZip"].isin(selected_zips)) &
    (df["UnitCategory"].isin(selected_categories)) &
    (df["RegisteredDate"].dt.date >= start_date) &
    (df["RegisteredDate"].dt.date <= end_date)
].copy()

# ----------------------------
# Chart 1: Density Map
# ----------------------------
st.subheader("Density of Rental Properties")

fig_map = px.density_mapbox(
    df_filtered,
    lat="Latitude",
    lon="Longitude",
    z="RentalHousingUnits",
    radius=8,
    center=dict(lat=47.6062, lon=-122.3321),
    zoom=10,
    mapbox_style="carto-positron",
    title=None
)

fig_map.update_layout(
    height=650,
    margin=dict(l=0, r=0, t=0, b=0)
)

st.plotly_chart(fig_map, use_container_width=True)

# ----------------------------
# Row 2
# ----------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("Distribution of Rental Units Across Properties")

    fig_hist = px.histogram(
        df_filtered,
        x="RentalHousingUnits",
        nbins=40,
        title=None
    )

    fig_hist.update_layout(
        xaxis_title="Number of Rental Units",
        yaxis_title="Count"
    )

    # change to wider intervals like before
    fig_hist.update_traces(
        xbins=dict(start=0, end=max_units, size=20)
    )

    st.plotly_chart(fig_hist, use_container_width=True)

with col2:
    st.subheader("Top 10 Zip Codes by Number of Properties")

    zip_count = (
        df_filtered.groupby(["OriginalZip", "AreaName"])
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
        .head(10)
    )

    zip_count["ZipAreaLabel"] = zip_count["OriginalZip"] + " - " + zip_count["AreaName"]

    fig_zip = px.bar(
        zip_count,
        x="ZipAreaLabel",
        y="count",
        title=None
    )

    fig_zip.update_xaxes(type="category")
    fig_zip.update_layout(
        xaxis_title="Zip Code and Area",
        yaxis_title="Count"
    )

    st.plotly_chart(fig_zip, use_container_width=True)

# ----------------------------
# Row 3
# ----------------------------
col3, col4 = st.columns(2)

with col3:
    st.subheader("Monthly Rental Property Registrations")

    monthly = (
        df_filtered
        .groupby(df_filtered["RegisteredDate"].dt.to_period("M"))
        .size()
        .reset_index(name="count")
    )

    monthly["RegisteredDate"] = pd.to_datetime(monthly["RegisteredDate"].astype(str))
    monthly = monthly.sort_values("RegisteredDate")

    fig_time = px.line(
        monthly,
        x="RegisteredDate",
        y="count",
        title=None
    )

    fig_time.update_layout(
        xaxis_title="Registration Date",
        yaxis_title="Number of Registrations"
    )

    fig_time.update_xaxes(
        range=[monthly["RegisteredDate"].min(), monthly["RegisteredDate"].max()],
        dtick="M3",
        tickformat="%Y-%m"
    )

    st.plotly_chart(fig_time, use_container_width=True)

with col4:
    st.subheader("Registration Activity by Month and Weekday")

    heatmap_data = df_filtered.copy()
    heatmap_data["Month"] = heatmap_data["RegisteredDate"].dt.month_name().str[:3]
    heatmap_data["Weekday"] = heatmap_data["RegisteredDate"].dt.day_name()

    month_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                   "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    heatmap_count = (
        heatmap_data.groupby(["Weekday", "Month"])
        .size()
        .reset_index(name="count")
    )

    fig_heat = px.density_heatmap(
        heatmap_count,
        x="Month",
        y="Weekday",
        z="count",
        color_continuous_scale="Blues",
        title=None,
        text_auto=True,
        category_orders={
            "Month": month_order,
            "Weekday": weekday_order
        }
    )

    fig_heat.update_layout(
        xaxis_title="Month",
        yaxis_title="Day of Week"
    )

    st.plotly_chart(fig_heat, use_container_width=True)

# ----------------------------
# Notes and source
# ----------------------------
st.markdown("---")
st.markdown(
    """
    **Dashboard Notes:**  
    - The map shows where rental properties are concentrated across Seattle.  
    - The histogram shows the overall distribution of rental unit counts.  
    - The zip chart compares the areas with the highest number of properties.  
    - The time series shows how registration activity changes over time.  
    - The heatmap shows when activity is more concentrated by month and weekday.  
    """
)

st.markdown(
    """
    **Data Source:**  
    Seattle Open Data — Rental Property Registration dataset.  
    ZIP area labels were added to improve readability in the dashboard.
    """
)
