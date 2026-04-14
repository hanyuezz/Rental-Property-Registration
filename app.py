import streamlit as st
import pandas as pd
import plotly.express as px

# ----------------------------
# Page setup
# ----------------------------
st.set_page_config(page_title="Seattle Rental Property Dashboard", layout="wide")

st.title("Seattle Rental Property Dashboard")
st.markdown(
    """
    This dashboard explores rental property patterns in Seattle, focusing on location, 
    size distribution, area differences, and registration activity over time.
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

df = df.dropna(
    subset=["RegisteredDate", "RentalHousingUnits", "Latitude", "Longitude", "OriginalZip"]
)

# Clean zip codes: keep only 5-digit zip codes starting with 98
df["OriginalZip"] = df["OriginalZip"].astype(str).str.extract(r"(\d+)")[0]
df = df[df["OriginalZip"].str.len() == 5]
df = df[df["OriginalZip"].str.startswith("98")]

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
df["Year"] = df["RegisteredDate"].dt.year
df["Month"] = df["RegisteredDate"].dt.to_period("M").astype(str)

# ----------------------------
# Sidebar filters
# ----------------------------
st.sidebar.header("Filters")

max_units = int(df["RentalHousingUnits"].max())
unit_range = st.sidebar.slider(
    "Units Range",
    min_value=0,
    max_value=max_units,
    value=(0, 20)
)

zip_options = sorted(df["OriginalZip"].unique().tolist())
selected_zips = st.sidebar.multiselect(
    "Select Zip Codes",
    options=zip_options,
    default=zip_options
)

category_options = ["Small", "Medium", "Large"]
selected_categories = st.sidebar.multiselect(
    "Unit Category",
    options=category_options,
    default=category_options
)

# Apply filters
df_filtered = df[
    (df["RentalHousingUnits"] >= unit_range[0]) &
    (df["RentalHousingUnits"] <= unit_range[1]) &
    (df["OriginalZip"].isin(selected_zips)) &
    (df["UnitCategory"].isin(selected_categories))
].copy()

# ----------------------------
# Row 1
# ----------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("Density of Rental Properties")

    fig_map = px.density_mapbox(
        df_filtered,
        lat="Latitude",
        lon="Longitude",
        z="RentalHousingUnits",
        radius=12,
        center=dict(lat=47.6062, lon=-122.3321),
        zoom=10,
        mapbox_style="carto-positron",
        title=None
    )
    st.plotly_chart(fig_map, use_container_width=True)

with col2:
    st.subheader("Distribution of Rental Units")

    fig_hist = px.histogram(
        df_filtered[df_filtered["RentalHousingUnits"] <= 20],
        x="RentalHousingUnits",
        nbins=20,
        title=None
    )
    fig_hist.update_layout(
        xaxis_title="RentalHousingUnits",
        yaxis_title="Count"
    )
    st.plotly_chart(fig_hist, use_container_width=True)

# ----------------------------
# Row 2
# ----------------------------
col3, col4 = st.columns(2)

with col3:
    st.subheader("Top 10 Zip Codes by Number of Properties")

    zip_count = (
        df_filtered["OriginalZip"]
        .value_counts()
        .nlargest(10)
        .reset_index()
    )
    zip_count.columns = ["zip", "count"]
    zip_count = zip_count.sort_values("count", ascending=False)

    fig_zip = px.bar(
        zip_count,
        x="zip",
        y="count",
        title=None
    )
    fig_zip.update_xaxes(type="category")
    fig_zip.update_layout(
        xaxis_title="Zip Code",
        yaxis_title="Count"
    )
    st.plotly_chart(fig_zip, use_container_width=True)

with col4:
    st.subheader("Monthly Rental Property Registrations")

    monthly = (
        df_filtered
        .groupby(df_filtered["RegisteredDate"].dt.to_period("M"))
        .size()
        .reset_index(name="count")
    )
    monthly["RegisteredDate"] = pd.to_datetime(monthly["RegisteredDate"].astype(str))

    fig_time = px.area(
        monthly,
        x="RegisteredDate",
        y="count",
        title=None
    )
    fig_time.update_layout(
        xaxis_title="Registration Date",
        yaxis_title="Number of Registrations"
    )
    st.plotly_chart(fig_time, use_container_width=True)

# ----------------------------
# Row 3
# ----------------------------
st.subheader("Property Size Categories")

cat_count = df_filtered["UnitCategory"].value_counts().reset_index()
cat_count.columns = ["Category", "count"]

fig_cat = px.pie(
    cat_count,
    names="Category",
    values="count",
    title=None
)
st.plotly_chart(fig_cat, use_container_width=True)

# ----------------------------
# Bottom notes
# ----------------------------
st.markdown("---")
st.markdown(
    """
    **Dashboard Notes:**  
    - The map highlights where rental properties are concentrated across Seattle.  
    - The histogram focuses on smaller rental properties, where most observations are concentrated.  
    - The zip code chart compares the areas with the highest number of properties.  
    - The time series shows how registration activity changes across months.  
    - Filters on the left allow users to explore the data by unit size, zip code, and property size category.
    """
)
