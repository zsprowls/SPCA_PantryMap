import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os
from datetime import datetime, timedelta
import plotly.io as pio
import geopandas as gpd
from shared.utils import check_password, load_geojson
from shared.drive_utils import load_json_from_drive, load_csv_from_drive
import plotly.graph_objects as go
import folium
from streamlit_folium import folium_static
from folium.plugins import HeatMap

# Page config
st.set_page_config(
    page_title="Pet Pantry Client Map",
    page_icon="🐾",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .stSlider {
        width: 100% !important;
    }
    .year-display {
        position: absolute;
        bottom: 220px;
        left: 100px;
        font-size: 48px;
        font-weight: bold;
        color: #000000;
        text-shadow: 2px 2px 4px rgba(255,255,255,0.8);
        z-index: 1000;
        pointer-events: none;
    }
    .stSlider [data-testid="stTickBar"],
    .stSlider [data-testid="stMarkdownContainer"],
    .stSlider .rc-slider-mark,
    .stSlider .rc-slider-step,
    .stSlider .rc-slider-dot,
    .stSlider .rc-slider-mark-text {
        display: none !important;
    }
    .stSlider .rc-slider-tooltip,
    .stSlider .rc-slider-tooltip-content,
    .stSlider .rc-slider-tooltip-placement-top {
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Check authentication
if not check_password():
    st.stop()

# Load data
@st.cache_data
def load_data():
    try:
        return load_json_from_drive('processed_pantry_data.json')
    except Exception as e:
        st.error(f"Error loading pantry data: {str(e)}")
        st.stop()

# Main app
st.title("Pet Pantry Client Map")

# Load data
data = load_data()
if not data:
    st.error("No data found. Please ensure processed_pantry_data.json exists in Google Drive.")
    st.stop()

# Convert to DataFrame
df = pd.DataFrame(data)

# Load original CSV for ZIP codes
try:
    csv_df = load_csv_from_drive('PantryMap.csv')
except Exception as e:
    st.error(f"Error loading PantryMap.csv: {str(e)}")
    st.stop()

# Convert date strings to datetime
df['date'] = pd.to_datetime(df['date'])

# Add PetPoint link column
base_url = "https://sms.petpoint.com/sms3/enhanced/person/"
def format_petpoint_link(pid):
    if pd.isna(pid):
        return None
    # Extract digits and remove leading zeros
    digits = ''.join(filter(str.isdigit, str(pid)))
    digits = digits.lstrip('0')
    return base_url + digits if digits else None

df['petpoint_link'] = df['person_id'].apply(format_petpoint_link)

# Create controls in a single row
col1, col2 = st.columns([3, 1])

with col1:
    # Create year selector
    min_date = df['date'].min().date()
    max_date = df['date'].max().date()
    years = range(min_date.year, max_date.year + 1)
    year_options = list(years)
    
    if 'selected_year' not in st.session_state:
        st.session_state['selected_year'] = max_date.year
    
    selected_year = st.selectbox(
        "Select Year",
        options=year_options,
        index=len(year_options)-1,
        label_visibility="collapsed"
    )
    st.session_state['selected_year'] = selected_year
    
    # Set the selected date to the end of the selected year, or max_date if current year
    if selected_year == max_date.year:
        selected_date = max_date
    else:
        selected_date = datetime(selected_year, 12, 31).date()
    
    # Display the full date below the selector
    st.markdown(f"<div style='text-align: center; font-size: 1.2em;'>{selected_date.strftime('%B %d, %Y')}</div>", unsafe_allow_html=True)

with col2:
    # Add visualization type selector
    map_type = st.radio(
        "Map Type",
        ["Markers", "Heatmap", "Choropleth"],
        horizontal=True
    )

# Filter data for selected date
filtered_df = df[df['date'].dt.date <= selected_date]

# Create map based on selected type
if map_type == "Choropleth":
    geo = load_geojson()
    
    # Filter CSV data by date
    csv_df['Association Creation Date'] = pd.to_datetime(csv_df['Association Creation Date'])
    filtered_csv = csv_df[csv_df['Association Creation Date'].dt.date <= selected_date]
    
    # Count clients per zip code from the filtered CSV data
    zip_counts = filtered_csv['Postal Code'].value_counts().reset_index()
    zip_counts.columns = ['ZCTA5CE10', 'count']
    
    # Create the choropleth map
    fig = px.choropleth_mapbox(
        zip_counts,
        geojson=geo,
        locations='ZCTA5CE10',
        featureidkey="properties.ZCTA5CE10",
        color='count',
        color_continuous_scale="YlOrRd",
        mapbox_style="carto-positron",
        zoom=7,
        center={"lat": 42.8864, "lon": -78.8784},
        opacity=0.7,
        title=f"Pet Pantry Clients by ZIP Code as of {selected_date.strftime('%B %d, %Y')}"
    )
    
    fig.update_layout(
        mapbox_bounds={
            "west": -80.5,
            "east": -77.5,
            "south": 41.8,
            "north": 43.4
        },
        margin={"r":0,"t":30,"l":0,"b":0}
    )
    
    st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})

elif map_type == "Heatmap":
    # Create a folium map centered on Erie County
    m = folium.Map(location=[42.9, -78.8], zoom_start=10, tiles='CartoDB positron')
    # Prepare heat data
    heat_data = filtered_df[['lat', 'lng']].dropna().values.tolist()
    HeatMap(heat_data, radius=18, blur=15, min_opacity=0.2, max_zoom=1).add_to(m)
    folium_static(m, width=800, height=650)

else:
    # Create scatter map for markers or heatmap
    if map_type == "Heatmap":
        # Create a heatmap using scatter_mapbox with size and opacity
        fig = px.scatter_mapbox(
            filtered_df,
            lat="lat",
            lon="lng",
            color_discrete_sequence=["#FF5733"],
            zoom=9,
            height=650,
            hover_data={
                "name": True,
                "address_type": True,
                "petpoint_link": True,
                "lat": False,
                "lng": False
            }
        )
        
        # Create heat data with weighted points
        heat_data = []
        for _, row in filtered_df.iterrows():
            # Add multiple points to increase intensity
            for _ in range(3):  # Adjust this number to control heat intensity
                heat_data.append([row['lat'], row['lng']])
        
        # Add heatmap layer
        fig.add_trace(go.Scattermapbox(
            lat=[point[0] for point in heat_data],
            lon=[point[1] for point in heat_data],
            mode='markers',
            marker=dict(
                size=15,
                color='red',
                opacity=0.3,
                sizemode='diameter',
                sizeref=2,
                sizemin=4
            ),
            hoverinfo='skip',
            name='Heatmap'
        ))
        
        # Update layout for heatmap
        fig.update_layout(
            mapbox_style="carto-positron",
            margin={"r":0,"t":0,"l":0,"b":0},
            mapbox_bounds={
                "west": -80.0,
                "east": -77.8,
                "south": 42.0,
                "north": 43.6
            }
        )
        
        # Add colorbar
        fig.update_traces(
            marker=dict(
                colorscale='RdBu',
                showscale=True,
                colorbar=dict(
                    title="Density",
                    titleside="right",
                    ticks="outside"
                )
            )
        )
    else:  # Markers
        fig = px.scatter_mapbox(
            filtered_df,
            lat="lat",
            lon="lng",
            color_discrete_sequence=["#FF5733"],
            zoom=9,
            height=650,
            hover_data={
                "name": True,
                "address_type": True,
                "petpoint_link": True,
                "lat": False,
                "lng": False
            }
        )
    
    fig.update_layout(
        mapbox_style="carto-positron",
        margin={"r":0,"t":0,"l":0,"b":0},
        mapbox_bounds={
            "west": -80.0,
            "east": -77.8,
            "south": 42.0,
            "north": 43.6
        }
    )
    
    # Add scatter points for each location
    fig.add_trace(go.Scattermapbox(
        lat=filtered_df['lat'],
        lon=filtered_df['lng'],
        mode='markers',
        marker=dict(
            size=10,
            color='red',
            opacity=0.7
        ),
        text=filtered_df.apply(lambda row: f"<a href='{row['petpoint_link']}' target='_blank'>{row['name']}</a><br>Address Type: {row['address_type']}", axis=1),
        hoverinfo='text',
        name='Pet Pantry Locations'
    ))
    
    st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})

# Add year display
st.markdown(f'<div class="year-display">{selected_date.year}</div>', unsafe_allow_html=True)

# Statistics
st.sidebar.header("Statistics")
st.sidebar.metric("Total Clients", len(filtered_df))
st.sidebar.metric("Unique Locations", filtered_df['name'].nunique())

# Data table
if st.sidebar.checkbox("Show Data Table"):
    st.dataframe(filtered_df[['name', 'date', 'address_type', 'person_id']].sort_values('date', ascending=False)) 
    
