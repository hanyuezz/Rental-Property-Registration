import streamlit as st
import plotly.express as px
import pandas as pd

# 1. Page Configuration
st.set_page_config(page_title="Seattle Crime Explorer", layout="wide")

st.title("Seattle Crime Data Interactive Explorer (2025-Present)")
st.markdown("This dashboard focuses on recent crime patterns in Seattle (2025-2026).")

# 2. Load Data
@st.cache_data
def load_data():
    data = pd.read_csv('seattle_crime_small.csv')
    data['Report DateTime'] = pd.to_datetime(data['Report DateTime'])
    data['Year'] = data['Report DateTime'].dt.year
    return data

df = load_data()

# 3. Sidebar Controls
st.sidebar.header("Filter Controls")

# Year Slider
years = sorted(df['Year'].unique())
selected_year = st.sidebar.select_slider(
    "Select Year", 
    options=years, 
    value=max(years)
)

# Crime Type Multiselect
crime_options = sorted(df['Offense Parent Group'].unique())
selected_crimes = st.sidebar.multiselect(
    "Select Crime Categories",
    options=crime_options,
    default=crime_options[:5]
)

# Apply Filters
mask = (df['Year'] == selected_year) & (df['Offense Parent Group'].isin(selected_crimes))
filtered_df = df[mask]

# 4. Key Metrics
m1, m2, m3 = st.columns(3)
m1.metric("Total Incidents", f"{len(filtered_df):,}")
m2.metric("Active Neighborhoods (MCPP)", filtered_df['MCPP'].nunique())
m3.metric("Selected Year", selected_year)

st.divider()

# 5. Interactive Charts
col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("Incident Frequency by Category")
    counts = filtered_df['Offense Parent Group'].value_counts().reset_index()
    fig_bar = px.bar(
        counts, 
        x='Offense Parent Group', 
        y='count', 
        color='Offense Parent Group',
        template="plotly_white"
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with col_right:
    st.subheader("Geographical Distribution")
    fig_map = px.scatter_mapbox(
        filtered_df, 
        lat="Latitude", 
        lon="Longitude",
        color="Offense Parent Group",
        hover_name="Offense", 
        mapbox_style="carto-positron", 
        zoom=10
    )
    st.plotly_chart(fig_map, use_container_width=True)

# 6. Raw Data Table
with st.expander("View Filtered Raw Data"):
    st.dataframe(filtered_df.sort_values('Report DateTime', ascending=False))
