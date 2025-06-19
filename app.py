import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
import json
import geopandas as gpd
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from streamlit_folium import st_folium
import os

# Force light mode and set page config with expanded sidebar
st.set_page_config(
    page_title="SPCA Client Density & Food Pantry Map", 
    page_icon="🐾", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Main app code
st.markdown(
    """
    <style>
    body, .stApp {
        background-color: #f8fafc !important;
        color: #222 !important;
    }
    .block-container {
        background-color: #ffffff !important;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        padding: 2rem 2rem 1rem 2rem;
    }
    .stButton>button {
        background-color: #7ac143 !important;
        color: white !important;
        border-radius: 8px;
        border: none;
        font-weight: bold;
    }
    .st-bb, .st-cq, .st-cv, .st-cw, .st-cx, .st-cy, .st-cz {
        background-color: #f8fafc !important;
    }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #5E6D40 !important;
    }
    .centered-title {
        text-align: center;
        margin-bottom: 0.5em;
        color: #5E6D40 !important;
    }
    .centered-desc {
        text-align: center;
        font-size: 1.1em;
        color: #444;
        margin-top: 0;
        margin-bottom: 2em;
    }
    /* Prevent map flashing/haze */
    .folium-map {
        background-color: transparent !important;
    }
    .leaflet-container {
        background-color: transparent !important;
    }
    .leaflet-pane {
        background-color: transparent !important;
    }
    /* Prevent white flash during map interactions */
    .leaflet-fade-anim .leaflet-tile,
    .leaflet-fade-anim .leaflet-popup {
        opacity: 1 !important;
        transition: none !important;
    }
    .leaflet-zoom-anim .leaflet-zoom-animated {
        transition: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Add logo
st.image("https://bufny.wpenginepowered.com/wp-content/uploads/2020/07/cropped-SPCAlogo_horiz_notagline_color.jpg", width=350)

# Centered title and description
st.markdown("""
<h2 class='centered-title'>SPCA Client Density & Human Food Pantry Map</h2>
<p class='centered-desc'>This map shows human food pantry locations (green pins) with colored areas indicating SPCA client density by ZIP code area.</p>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    try:
        # Load pantry locations
        pantry_df = pd.read_csv('map_data/geocoded_pantry_locations.csv')
        
        # Filter out NaN values in latitude/longitude
        pantry_df = pantry_df.dropna(subset=['latitude', 'longitude'])
        
        # Additional validation: ensure coordinates are valid numbers and within reasonable bounds
        pantry_df = pantry_df[
            (pantry_df['latitude'].between(40, 45)) &  # Erie County is roughly 42-43°N
            (pantry_df['longitude'].between(-80, -78))  # Erie County is roughly -79°W
        ]
        
        # Load survey data for ZIP boundaries
        with open('map_data/erie_survey_zips.geojson', 'r') as f:
            survey_data = json.load(f)
        
        # Load PantryMap data for client counts
        pantry_map = pd.read_csv('map_data/PantryMap.csv')
        
        # Clean ZIP codes
        def clean_zip(zipcode):
            try:
                return str(int(float(zipcode))).zfill(5)
            except:
                return None
        
        pantry_map['Postal Code'] = pantry_map['Postal Code'].apply(clean_zip)
        zip_counts = pantry_map['Postal Code'].value_counts().reset_index()
        zip_counts.columns = ['ZCTA5CE10', 'client_count']
        
        return pantry_df, survey_data, zip_counts
    except Exception as e:
        st.error(f"❌ Error loading data: {e}")
        return None, None, None

pantry_df, survey_data, zip_counts = load_data()

if pantry_df is not None and survey_data is not None and zip_counts is not None:
    # Create map
    m = folium.Map(
        location=[42.8864, -78.8784], 
        zoom_start=9,
        prefer_canvas=True,
        zoom_control=True,
        scrollWheelZoom=True,
        dragging=True,
        touchZoom=True,
        doubleClickZoom=True,
        boxZoom=True,
        keyboard=True,
        tap=True
    )
    
    # Add pantry markers with clustering
    marker_cluster = MarkerCluster().add_to(m)
    
    # Build detailed hover text for each pantry
    pantry_df['hover_text'] = (
        '<b>' + pantry_df['name'].astype(str) + '</b><br>' +
        pantry_df['address'].astype(str) + '<br>' +
        'Phone: ' + pantry_df['phone'].astype(str) + '<br>' +
        'Hours: ' + pantry_df['hours'].astype(str)
    )
    
    for idx, row in pantry_df.iterrows():
        try:
            lat = float(row['latitude'])
            lon = float(row['longitude'])
            
            # Double-check coordinates are valid
            if pd.isna(lat) or pd.isna(lon) or not (40 <= lat <= 45) or not (-80 <= lon <= -78):
                continue
            
            # Add marker to cluster with original working tooltip
            folium.Marker(
                location=[lat, lon],
                popup=folium.Popup(row['hover_text'], max_width=300),
                tooltip=folium.Tooltip(row['hover_text'], sticky=True),
                icon=folium.Icon(color='green', icon='shopping-cart', prefix='fa')
            ).add_to(marker_cluster)
            
        except (ValueError, TypeError):
            continue
    
    # Create choropleth with ZIP code boundaries
    try:
        # Create GeoDataFrame from survey data
        gdf = gpd.GeoDataFrame.from_features(survey_data['features'])
        gdf['ZCTA5CE10'] = gdf['ZCTA5CE10'].astype(str)
        
        # Merge with client count data
        gdf = gdf.merge(zip_counts, on='ZCTA5CE10', how='left')
        gdf['client_count'] = gdf['client_count'].fillna(0)
        
        # Add individual GeoJson polygons instead of Choropleth
        def style_function(feature):
            client_count = feature['properties']['client_count']
            if client_count > 100:
                return {'fillColor': '#d73027', 'color': '#000000', 'weight': 2, 'fillOpacity': 0.8}
            elif client_count > 50:
                return {'fillColor': '#f46d43', 'color': '#000000', 'weight': 2, 'fillOpacity': 0.7}
            elif client_count > 20:
                return {'fillColor': '#fdae61', 'color': '#000000', 'weight': 2, 'fillOpacity': 0.6}
            elif client_count > 5:
                return {'fillColor': '#fee08b', 'color': '#000000', 'weight': 2, 'fillOpacity': 0.5}
            elif client_count > 0:
                return {'fillColor': '#ffffcc', 'color': '#000000', 'weight': 2, 'fillOpacity': 0.4}
            else:
                return {'fillColor': '#ffffff', 'color': '#666666', 'weight': 2, 'fillOpacity': 0.1}
        
        folium.GeoJson(
            gdf.__geo_interface__,
            style_function=style_function,
            tooltip=folium.GeoJsonTooltip(
                fields=['ZCTA5CE10', 'client_count'],
                aliases=['ZIP Code', 'SPCA Clients'],
                localize=True,
                sticky=False,
                labels=True
            )
        ).add_to(m)
        
    except Exception as e:
        st.error(f"❌ Choropleth failed: {e}")
    
    # Display map with proper sizing
    st_folium(m, use_container_width=True, height=600)
    
    # Add legend
    st.markdown("---")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Map Legend")
        st.markdown("""
        **🛒 Food Pantry Locations** - Green shopping cart icons (clustered when zoomed out)
        """)
        
        st.markdown("**SPCA Client Density by ZIP Code (Choropleth):**")
        st.markdown("""
        The colored areas show ZIP code boundaries with SPCA client density:
        - **Dark Red** = High client density
        - **Light Red** = Medium client density  
        - **Very Light Red** = Low client density
        - **White** = No clients
        """)
    
    with col2:
        st.subheader("Data Summary")
        st.write(f"**🍽️ Pantry Locations:** {len(pantry_df)}")
        st.write(f"**🗺️ Survey Zip Codes:** {len(survey_data['features'])}")
        
        # Calculate total clients
        total_clients = sum(
            feature['properties'].get('client_count', 0) 
            for feature in survey_data['features']
        )
        st.write(f"**👥 Total SPCA Clients:** {total_clients:,}")
else:
    st.error("Failed to load data. Please check your data files.")

# --- SIDEBAR: Adoption/Support Links ---
with st.sidebar:
    st.markdown("""
    <a class="fasc-button fasc-size-large fasc-type-flat fasc-rounded-medium fasc-style-bold" style="display:block; background-color: #512a44; color: #ffffff; text-align:center; padding: 0.75em 1em; border-radius: 8px; font-size:1.1em; font-weight:bold; margin-bottom:1em; text-decoration:none;" target="_blank" href="https://yourspca.org/who-we-are/hours-locations/" rel="noopener">Hours & Location</a>
    <a class="fasc-button fasc-size-large fasc-type-flat fasc-rounded-medium fasc-style-bold" style="display:block; background-color: #512a44; color: #ffffff; text-align:center; padding: 0.75em 1em; border-radius: 8px; font-size:1.1em; font-weight:bold; margin-bottom:1em; text-decoration:none;" target="_blank" href="https://yourspca.org/what-we-do/animal-rescue-cruelty-investigations/" rel="noopener">Report Animal Cruelty</a>
    <a class="fasc-button fasc-size-large fasc-type-flat fasc-rounded-medium fasc-style-bold" style="display:block; background-color: #512a44; color: #ffffff; text-align:center; padding: 0.75em 1em; border-radius: 8px; font-size:1.1em; font-weight:bold; margin-bottom:1em; text-decoration:none;" target="_blank" href="https://yourspca.org/assistance-with-veterinary-care/" rel="noopener">Assistance with Veterinary Care</a>
    <a class="fasc-button fasc-size-large fasc-type-flat fasc-rounded-medium fasc-style-bold" style="display:block; background-color: #512a44; color: #ffffff; text-align:center; padding: 0.75em 1em; border-radius: 8px; font-size:1.1em; font-weight:bold; margin-bottom:1em; text-decoration:none;" target="_blank" href="https://yourspca.org/vaccine-microchip-clinics/" rel="noopener">Vaccine & Microchip Clinics</a>
    <a class="fasc-button fasc-size-large fasc-type-flat fasc-rounded-medium fasc-style-bold" style="display:block; background-color: #512a44; color: #ffffff; text-align:center; padding: 0.75em 1em; border-radius: 8px; font-size:1.1em; font-weight:bold; margin-bottom:1em; text-decoration:none;" target="_blank" href="https://yourspca.org/communityresources/" rel="noopener">Other Community Resources</a>
    <a class="fasc-button fasc-size-large fasc-type-flat fasc-rounded-medium fasc-style-bold" style="display:block; background-color: #653B55; color: #ffffff; text-align:center; padding: 0.75em 1em; border-radius: 8px; font-size:1.1em; font-weight:bold; margin-bottom:1em; text-decoration:none;" target="_blank" href="https://yourspca.org/petfoodpantry/" rel="noopener">Learn more about the SPCA Pet Food Pantry</a>
    <a class="fasc-button fasc-size-large fasc-type-flat fasc-rounded-medium fasc-style-bold" style="display:block; background-color: #5E6D40; color: #ffffff; text-align:center; padding: 0.75em 1em; border-radius: 8px; font-size:1.1em; font-weight:bold; margin-bottom:1em; text-decoration:none;" target="_blank" href="https://forms.gle/aR9szeeWpKieq7ZJ9" rel="noopener">Please use this form to submit an electronic request for pet food assistance</a>
    """, unsafe_allow_html=True) 