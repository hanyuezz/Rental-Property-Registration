# Seattle Rental Property Dashboard

## Project Overview
This project analyzes rental property registration data in the City of Seattle using an interactive dashboard built with Streamlit. The goal is to explore how rental properties are distributed across location, property size, and time, and to identify patterns that can support urban planning and housing policy decisions.

The dashboard allows users to explore the data dynamically through filters and multiple visualizations.

---

## Dataset
- Source: Seattle Open Data – Rental Property Registration dataset
- Time Range: 2024 – Present
- Size: ~28,000 records
- Granularity: Property-level data

### Key Fields
- `RentalHousingUnits`: Number of rental units per property
- `RegisteredDate`: Date of registration
- `OriginalZip`: ZIP code
- `Latitude`, `Longitude`: Location coordinates

---

## Data Processing
The following preprocessing steps were performed:

- Converted date fields into datetime format  
- Converted numeric columns (units, latitude, longitude)  
- Cleaned ZIP codes and ensured consistent formatting  
- Corrected invalid ZIP codes (e.g., 89133 → 98133)  
- Created property size categories:
  - Small (1–5 units)
  - Medium (6–20 units)
  - Large (21+ units)
- Mapped ZIP codes to readable Seattle area names  

---

## Dashboard Features

### Visualizations
The dashboard includes five main visualizations:

1. **Density Map**
   - Shows spatial concentration of rental properties

2. **Histogram (Unit Distribution)**
   - Displays distribution of rental unit sizes using wider bins

3. **Top ZIP Code Bar Chart**
   - Compares property counts across areas

4. **Time Series Chart**
   - Shows registration activity over time

5. **Heatmap (Month vs Weekday)**
   - Highlights temporal activity patterns

---

### Interactive Filters
Users can filter the data by:

- Unit range  
- ZIP code  
- Property category (Small / Medium / Large)  
- Date range  

These filters allow flexible exploration and deeper analysis.

---

## Key Insights
- Rental properties are concentrated in specific areas such as North Seattle  
- Most properties are small or medium-sized  
- Registration activity varies over time, with higher activity in mid-year  
- Some ZIP code areas consistently have higher property counts  

---

## Limitations
- Data only includes records from 2024 onward  
- Only registered properties are included  
- ZIP-to-area mapping is approximate  
- No pricing or occupancy data available  

---

## How to Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
