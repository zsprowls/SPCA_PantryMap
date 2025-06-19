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

# Force light mode and set page config
st.set_page_config(page_title="SPCA Client Density & Food Pantry Map", page_icon="🐾", layout="wide")

# File selector at the top
st.sidebar.title("App Selector")
app_choice = st.sidebar.selectbox(
    "Choose which app to run:",
    ["Main App (Circles & Pins)", "Simple Folium Test", "Plotly Map Test"]
)

if app_choice == "Simple Folium Test":
    # Import and run the simple folium test
    import simple_map_test
elif app_choice == "Plotly Map Test":
    # Import and run the plotly test
    import plotly_map_test
else:
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
        </style>
        """,
        unsafe_allow_html=True
    )

    # Add logo
    st.image("https://bufny.wpenginepowered.com/wp-content/uploads/2020/07/cropped-SPCAlogo_horiz_notagline_color.jpg", width=350)
    
    # Centered title and description
    st.markdown("""
    <h2 class='centered-title'>SPCA Client Density & Human Food Pantry Map</h2>
    <p class='centered-desc'>This map shows human food pantry locations (red pins) with colored circles indicating SPCA client density by ZIP code area.</p>
    """, unsafe_allow_html=True)

    # Load data
    @st.cache_data
    def load_data():
        try:
            # Load pantry locations
            pantry_df = pd.read_csv('map_data/geocoded_pantry_locations.csv')
            st.write(f"✅ Loaded {len(pantry_df)} pantry locations")
            
            # Load survey data
            with open('map_data/erie_survey_zips.geojson', 'r') as f:
                survey_data = json.load(f)
            st.write(f"✅ Loaded survey data with {len(survey_data['features'])} zip codes")
            
            return pantry_df, survey_data
        except Exception as e:
            st.error(f"❌ Error loading data: {e}")
            return None, None
    
    pantry_df, survey_data = load_data()
    
    if pantry_df is not None and survey_data is not None:
        # Create map
        m = folium.Map(location=[42.8864, -78.8784], zoom_start=9)
        
        # Add pantry markers
        for idx, row in pantry_df.iterrows():
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=f"<b>{row['name']}</b><br>{row['address']}",
                icon=folium.Icon(color='red', icon='info-sign')
            ).add_to(m)
        
        # Add colored circles for survey data
        for feature in survey_data['features']:
            properties = feature['properties']
            geometry = feature['geometry']
            
            if geometry['type'] == 'Polygon':
                coordinates = geometry['coordinates'][0]
                # Convert to lat/lon pairs
                lat_lon_pairs = [[coord[1], coord[0]] for coord in coordinates]
                
                # Color based on client count
                client_count = properties.get('client_count', 0)
                if client_count > 100:
                    color = 'red'
                elif client_count > 50:
                    color = 'orange'
                elif client_count > 20:
                    color = 'yellow'
                else:
                    color = 'green'
                
                folium.Polygon(
                    locations=lat_lon_pairs,
                    color=color,
                    fill=True,
                    fill_opacity=0.3,
                    popup=f"Zip: {properties.get('zip_code', 'N/A')}<br>Clients: {client_count}"
                ).add_to(m)
        
        # Display map
        st_folium(m, width=800, height=600)
        
        # Show data summary
        st.subheader("Data Summary")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Pantry Locations:** {len(pantry_df)}")
        with col2:
            st.write(f"**Survey Zip Codes:** {len(survey_data['features'])}")
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

# Load the geocoded pantry data
pantry_data = pd.read_csv('map_data/geocoded_pantry_locations.csv')

# Filter out NaN lat/lon
pantry_data = pantry_data.dropna(subset=['latitude', 'longitude'])

# Build detailed hover text for each pantry
pantry_data['hover_text'] = (
    '<b>' + pantry_data['name'].astype(str) + '</b><br>' +
    pantry_data['address'].astype(str) + '<br>' +
    'Phone: ' + pantry_data['phone'].astype(str) + '<br>' +
    'Hours: ' + pantry_data['hours'].astype(str)
)

# Find nearby pantries if requested
nearby_pantries = pd.DataFrame()
user_location = None

# Load the Erie County zip codes GeoJSON
with open('map_data/erie_survey_zips.geojson', 'r') as f:
    erie_zips = json.load(f)

# Load the PantryMap data (Person ID and Postal Code)
pantry_map = pd.read_csv('map_data/PantryMap.csv')

def clean_zip(zipcode):
    try:
        return str(int(float(zipcode))).zfill(5)
    except:
        return None

pantry_map['Postal Code'] = pantry_map['Postal Code'].apply(clean_zip)

# Count total Person IDs per ZIP code
zip_counts = pantry_map['Postal Code'].value_counts().reset_index()
zip_counts.columns = ['ZCTA5CE10', 'count']

# Create a GeoDataFrame from the GeoJSON
gdf = gpd.GeoDataFrame.from_features(erie_zips['features'])
gdf['ZCTA5CE10'] = gdf['ZCTA5CE10'].astype(str)
gdf = gdf.merge(zip_counts, on='ZCTA5CE10', how='left')
gdf['count'] = gdf['count'].fillna(0)

# Create a Folium map centered on Erie County
m = folium.Map(location=[42.8864, -78.8784], zoom_start=9, tiles='OpenStreetMap')

# Add colored circles to show ZIP code data (more reliable than choropleth)
try:
    st.write(f"Creating ZIP code visualization with {len(gdf)} ZIP codes...")
    st.write(f"Sample data: {gdf[['ZCTA5CE10', 'count']].head()}")
    
    # Add colored circles for ZIP codes with data
    st.write("Adding colored circles for ZIP codes...")
    for _, row in gdf.iterrows():
        if row['count'] > 0:  # Only show ZIP codes with data
            # Get the center of the polygon
            center = row['geometry'].centroid
            # Color based on count
            if row['count'] > 10:
                color = 'red'
                radius = 2000
            elif row['count'] > 5:
                color = 'orange'
                radius = 1500
            else:
                color = 'yellow'
                radius = 1000
            
            folium.Circle(
                location=[center.y, center.x],
                radius=radius,
                color=color,
                fill=True,
                fill_opacity=0.6,
                popup=f"ZIP: {row['ZCTA5CE10']}<br>Client Count: {int(row['count'])}",
                tooltip=f"ZIP {row['ZCTA5CE10']}: {int(row['count'])} clients"
            ).add_to(m)
    
    st.success("✅ ZIP code visualization added successfully!")
    
except Exception as e:
    st.error(f"❌ ZIP code visualization failed: {e}")
    st.write("Continuing with just the pins...")

# Add clustered pantry pins with hover tooltips
marker_cluster = MarkerCluster().add_to(m)
for _, row in pantry_data.iterrows():
    marker = folium.Marker(
        location=[row['latitude'], row['longitude']],
        popup=folium.Popup(row['hover_text'], max_width=300),
        tooltip=folium.Tooltip(row['hover_text'], sticky=True),
        icon=folium.Icon(color='green', icon='shopping-cart', prefix='fa')
    )
    if not nearby_pantries.empty and row['name'] in nearby_pantries['name'].values:
        marker.add_to(marker_cluster)
        folium.Circle(
            location=[row['latitude'], row['longitude']],
            radius=250,
            color='#7ac143',
            fill=True,
            fill_opacity=0.2
        ).add_to(m)
    else:
        marker.add_to(marker_cluster)

# Add user location marker if found
if user_location:
    folium.Marker(
        location=user_location,
        icon=folium.Icon(color='blue', icon='user', prefix='fa'),
        popup="Your Location"
    ).add_to(m)

# Add layer control
folium.LayerControl().add_to(m)

# Display the map
try:
    st.write("Rendering map...")
    st_folium(m, width=1400, height=650, returned_objects=[])
    st.success("✅ Map rendered successfully!")
except Exception as e:
    st.error(f"Error displaying map: {str(e)}")
    st.info("Please refresh the page or try again later.")
    # Fallback: show map data as text
    st.write("Map data loaded successfully:")
    st.write(f"Number of pantry locations: {len(pantry_data)}")
    st.write(f"Number of ZIP codes: {len(gdf)}")
    st.write(f"ZIP code data sample: {gdf[['ZCTA5CE10', 'count']].head()}")

# Show nearby pantries as a table if found
if not nearby_pantries.empty:
    st.markdown("<h3 style='text-align:center; color:#653B55;'>Nearby Food Pantries</h3>", unsafe_allow_html=True)
    st.dataframe(nearby_pantries[['name', 'address', 'phone', 'hours', 'distance_miles']].rename(columns={'name':'Name','address':'Address','phone':'Phone','hours':'Hours','distance_miles':'Distance (miles)'}).reset_index(drop=True)) 