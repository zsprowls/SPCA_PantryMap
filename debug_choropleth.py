import streamlit as st
import pandas as pd
import folium
import json
import geopandas as gpd

st.title("Choropleth Debug Tool")

# Test 1: Load and examine GeoJSON
st.header("Test 1: GeoJSON Loading")
try:
    with open('map_data/erie_survey_zips.geojson', 'r') as f:
        erie_zips = json.load(f)
    st.success(f"✅ GeoJSON loaded successfully")
    st.write(f"Number of features: {len(erie_zips['features'])}")
    st.write(f"First feature properties: {erie_zips['features'][0]['properties']}")
except Exception as e:
    st.error(f"❌ GeoJSON loading failed: {e}")

# Test 2: Load and examine CSV data
st.header("Test 2: CSV Data Loading")
try:
    pantry_map = pd.read_csv('map_data/PantryMap.csv')
    st.success(f"✅ CSV loaded successfully")
    st.write(f"CSV shape: {pantry_map.shape}")
    st.write(f"CSV columns: {list(pantry_map.columns)}")
    st.write(f"Sample data:")
    st.write(pantry_map.head())
except Exception as e:
    st.error(f"❌ CSV loading failed: {e}")

# Test 3: Data cleaning and merging
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
    
    st.success(f"✅ Data processing successful")
    st.write(f"Unique ZIP codes: {len(zip_counts)}")
    st.write(f"Sample ZIP counts:")
    st.write(zip_counts.head())
except Exception as e:
    st.error(f"❌ Data processing failed: {e}")

# Test 4: GeoDataFrame creation
st.header("Test 4: GeoDataFrame Creation")
try:
    gdf = gpd.GeoDataFrame.from_features(erie_zips['features'])
    gdf['ZCTA5CE10'] = gdf['ZCTA5CE10'].astype(str)
    st.success(f"✅ GeoDataFrame created successfully")
    st.write(f"GeoDataFrame shape: {gdf.shape}")
    st.write(f"GeoDataFrame columns: {list(gdf.columns)}")
except Exception as e:
    st.error(f"❌ GeoDataFrame creation failed: {e}")

# Test 5: Data merging
st.header("Test 5: Data Merging")
try:
    merged_gdf = gdf.merge(zip_counts, on='ZCTA5CE10', how='left')
    merged_gdf['count'] = merged_gdf['count'].fillna(0)
    st.success(f"✅ Data merging successful")
    st.write(f"Merged shape: {merged_gdf.shape}")
    st.write(f"Count range: {merged_gdf['count'].min()} to {merged_gdf['count'].max()}")
    st.write(f"Non-zero counts: {(merged_gdf['count'] > 0).sum()}")
except Exception as e:
    st.error(f"❌ Data merging failed: {e}")

# Test 6: Simple choropleth
st.header("Test 6: Simple Choropleth")
try:
    m = folium.Map(location=[42.8864, -78.8784], zoom_start=9)
    
    # Try with minimal options
    folium.Choropleth(
        geo_data=merged_gdf.__geo_interface__,
        data=merged_gdf,
        columns=['ZCTA5CE10', 'count'],
        key_on='feature.properties.ZCTA5CE10',
        fill_color='YlOrRd',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name='Count'
    ).add_to(m)
    
    st.success("✅ Choropleth created successfully")
    st_folium(m, width=600, height=400)
except Exception as e:
    st.error(f"❌ Choropleth creation failed: {e}")
    st.write(f"Error details: {str(e)}")

st.write("---")
st.write("If Test 6 fails, the issue is with the choropleth rendering. If earlier tests fail, the issue is with data loading/processing.") 