import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import json
import geopandas as gpd

# Load the geocoded pantry data
pantry_data = pd.read_csv('Map Data/geocoded_pantry_locations.csv')

# Load the Erie County zip codes GeoJSON
with open('Map Data/erie_survey_zips.geojson', 'r') as f:
    erie_zips = json.load(f)

# Load the PantryMap data (Person ID and Postal Code)
pantry_map = pd.read_csv('Map Data/PantryMap.csv')

# Count total Person IDs per Postal Code
zip_counts = pantry_map.groupby('Postal Code').size().reset_index(name='count')

# Create a GeoDataFrame from the GeoJSON
gdf = gpd.GeoDataFrame.from_features(erie_zips['features'])
gdf['ZCTA5CE20'] = gdf['ZCTA5CE20'].astype(str)
gdf = gdf.merge(zip_counts, left_on='ZCTA5CE20', right_on='Postal Code', how='left')
gdf['count'] = gdf['count'].fillna(0)

# Create a Folium map centered on Erie County
m = folium.Map(location=[42.7684, -78.8871], zoom_start=9)

# Add the choropleth layer
folium.Choropleth(
    geo_data=gdf.__geo_interface__,
    name='choropleth',
    data=zip_counts,
    columns=['Postal Code', 'count'],
    key_on='feature.properties.ZCTA5CE20',
    fill_color='YlOrRd',
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name='Total Clients'
).add_to(m)

# Add pantry markers
for _, row in pantry_data.iterrows():
    if pd.notnull(row['latitude']) and pd.notnull(row['longitude']):
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=row['name'],
            icon=folium.Icon(color='green', icon='shopping-cart', prefix='fa')
        ).add_to(m)

# Display the map
folium_static(m) 