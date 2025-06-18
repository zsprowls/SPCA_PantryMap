import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
import json
import geopandas as gpd
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from streamlit_folium import st_folium

# --- BRANDING ---
# Force light mode
st.set_page_config(page_title="SPCA Client Density & Food Pantry Map", page_icon="🐾", layout="wide")
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

# Add logo (not centered)
st.image("https://bufny.wpenginepowered.com/wp-content/uploads/2020/07/cropped-SPCAlogo_horiz_notagline_color.jpg", width=350)
# Centered title and description
st.markdown("""
<h2 class='centered-title'>SPCA Client Density & Human Food Pantry Map</h2>
<p class='centered-desc'>This map overlays human food pantry locations (green pins) with a choropleth showing the density of SPCA clients by ZIP code.</p>
""", unsafe_allow_html=True)

# --- END BRANDING ---

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

# Add a simple marker to test if the map works
folium.Marker(
    location=[42.8864, -78.8784],
    popup="Erie County Center",
    icon=folium.Icon(color='red', icon='info-sign')
).add_to(m)

# Add layer control
folium.LayerControl().add_to(m)

cols = st.columns([1,2,1])
with cols[1]:
    try:
        # Try a simpler approach first
        st.write("Testing map display...")
        st_folium(m, width=1400, height=650, returned_objects=[])
    except Exception as e:
        st.error(f"Error displaying map: {str(e)}")
        st.info("Please refresh the page or try again later.")
        # Fallback: show map data as text
        st.write("Map data loaded successfully:")
        st.write(f"Number of pantry locations: {len(pantry_data)}")
        st.write(f"Number of ZIP codes: {len(gdf)}")

# Show nearby pantries as a table if found
if not nearby_pantries.empty:
    st.markdown("<h3 style='text-align:center; color:#653B55;'>Nearby Food Pantries</h3>", unsafe_allow_html=True)
    st.dataframe(nearby_pantries[['name', 'address', 'phone', 'hours', 'distance_miles']].rename(columns={'name':'Name','address':'Address','phone':'Phone','hours':'Hours','distance_miles':'Distance (miles)'}).reset_index(drop=True)) 