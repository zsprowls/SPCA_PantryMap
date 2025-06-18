import streamlit as st
import pandas as pd
import folium
import json
import geopandas as gpd
from streamlit_folium import st_folium

st.title("Minimal Choropleth Test - Real Data")

# Load the same data as the main app
try:
    # Load the Erie County zip codes GeoJSON
    with open('map_data/erie_survey_zips.geojson', 'r') as f:
        erie_zips = json.load(f)

    # Load the PantryMap data
    pantry_map = pd.read_csv('map_data/PantryMap.csv')

    def clean_zip(zipcode):
        try:
            return str(int(float(zipcode))).zfill(5)
        except:
            return None

    pantry_map['Postal Code'] = pantry_map['Postal Code'].apply(clean_zip)
    zip_counts = pantry_map['Postal Code'].value_counts().reset_index()
    zip_counts.columns = ['ZCTA5CE10', 'count']

    # Create a GeoDataFrame
    gdf = gpd.GeoDataFrame.from_features(erie_zips['features'])
    gdf['ZCTA5CE10'] = gdf['ZCTA5CE10'].astype(str)
    gdf = gdf.merge(zip_counts, on='ZCTA5CE10', how='left')
    gdf['count'] = gdf['count'].fillna(0)

    st.success("✅ Data loaded successfully!")
    st.write(f"ZIP codes: {len(gdf)}")
    st.write(f"Sample data: {gdf[['ZCTA5CE10', 'count']].head()}")

    # Create minimal map with just choropleth
    m = folium.Map(location=[42.8864, -78.8784], zoom_start=9, tiles='OpenStreetMap')
    
    # Add the choropleth
    folium.Choropleth(
        geo_data=gdf.__geo_interface__,
        name='Choropleth',
        data=gdf,
        columns=['ZCTA5CE10', 'count'],
        key_on='feature.properties.ZCTA5CE10',
        fill_color='YlOrRd',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name='Pet Pantry Client Count',
        nan_fill_color='white',
        highlight=True
    ).add_to(m)
    
    st.success("✅ Choropleth created!")
    
    # Display map
    st_folium(m, width=800, height=500)
    st.success("✅ Map displayed!")

except Exception as e:
    st.error(f"❌ Error: {e}")
    st.write(f"Error type: {type(e)}") 