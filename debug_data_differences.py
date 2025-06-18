import streamlit as st
import pandas as pd
import folium
import json
import geopandas as gpd
from streamlit_folium import st_folium
import sys

st.title("Data Processing Debug - Local vs Cloud")

st.write(f"Python version: {sys.version}")
st.write(f"Pandas version: {pd.__version__}")
st.write(f"GeoPandas version: {gpd.__version__}")

# Test 1: Load GeoJSON
st.header("Test 1: GeoJSON Loading")
try:
    with open('map_data/erie_survey_zips.geojson', 'r') as f:
        erie_zips = json.load(f)
    st.success("✅ GeoJSON loaded")
    st.write(f"Features: {len(erie_zips['features'])}")
    st.write(f"First feature properties: {erie_zips['features'][0]['properties']}")
except Exception as e:
    st.error(f"❌ GeoJSON failed: {e}")

# Test 2: Load CSV
st.header("Test 2: CSV Loading")
try:
    pantry_map = pd.read_csv('map_data/PantryMap.csv')
    st.success("✅ CSV loaded")
    st.write(f"Shape: {pantry_map.shape}")
    st.write(f"Columns: {list(pantry_map.columns)}")
    st.write(f"Sample: {pantry_map.head()}")
except Exception as e:
    st.error(f"❌ CSV failed: {e}")

# Test 3: Data Processing
st.header("Test 3: Data Processing")
try:
    def clean_zip(zipcode):
        try:
            return str(int(float(zipcode))).zfill(5)
        except:
            return None

    pantry_map['Postal Code'] = pantry_map['Postal Code'].apply(clean_zip)
    zip_counts = pantry_map['Postal Code'].value_counts().reset_index()
    zip_counts.columns = ['ZCTA5CE10', 'count']
    
    st.success("✅ Data processed")
    st.write(f"Unique ZIPs: {len(zip_counts)}")
    st.write(f"Sample counts: {zip_counts.head()}")
except Exception as e:
    st.error(f"❌ Processing failed: {e}")

# Test 4: GeoDataFrame Creation
st.header("Test 4: GeoDataFrame Creation")
try:
    gdf = gpd.GeoDataFrame.from_features(erie_zips['features'])
    st.success("✅ GeoDataFrame created")
    st.write(f"Shape: {gdf.shape}")
    st.write(f"Columns: {list(gdf.columns)}")
    st.write(f"Data types: {gdf.dtypes}")
except Exception as e:
    st.error(f"❌ GeoDataFrame failed: {e}")

# Test 5: Data Merging
st.header("Test 5: Data Merging")
try:
    gdf['ZCTA5CE10'] = gdf['ZCTA5CE10'].astype(str)
    merged_gdf = gdf.merge(zip_counts, on='ZCTA5CE10', how='left')
    merged_gdf['count'] = merged_gdf['count'].fillna(0)
    
    st.success("✅ Data merged")
    st.write(f"Merged shape: {merged_gdf.shape}")
    st.write(f"Count range: {merged_gdf['count'].min()} to {merged_gdf['count'].max()}")
    st.write(f"Non-zero counts: {(merged_gdf['count'] > 0).sum()}")
except Exception as e:
    st.error(f"❌ Merging failed: {e}")

# Test 6: GeoJSON Interface
st.header("Test 6: GeoJSON Interface")
try:
    geo_interface = merged_gdf.__geo_interface__
    st.success("✅ GeoJSON interface created")
    st.write(f"Type: {type(geo_interface)}")
    st.write(f"Features: {len(geo_interface['features'])}")
    st.write(f"First feature: {geo_interface['features'][0]}")
except Exception as e:
    st.error(f"❌ GeoJSON interface failed: {e}")

# Test 7: Simple Choropleth
st.header("Test 7: Simple Choropleth")
try:
    m = folium.Map(location=[42.8864, -78.8784], zoom_start=9)
    
    # Try with minimal parameters
    folium.Choropleth(
        geo_data=merged_gdf.__geo_interface__,
        data=merged_gdf,
        columns=['ZCTA5CE10', 'count'],
        key_on='feature.properties.ZCTA5CE10',
        fill_color='red',
        fill_opacity=0.7,
        line_opacity=0.2
    ).add_to(m)
    
    st.success("✅ Choropleth created")
    st_folium(m, width=600, height=400)
    st.success("✅ Map displayed")
    
except Exception as e:
    st.error(f"❌ Choropleth failed: {e}")
    st.write(f"Error type: {type(e)}")
    st.write(f"Error details: {str(e)}")

st.write("---")
st.write("This will help identify exactly where the difference between local and cloud occurs.") 