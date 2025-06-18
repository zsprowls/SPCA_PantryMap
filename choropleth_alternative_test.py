import streamlit as st
import pandas as pd
import folium
import json
import geopandas as gpd
from streamlit_folium import st_folium

st.title("Alternative Choropleth Test")

# Load the same data
with open('map_data/erie_survey_zips.geojson', 'r') as f:
    erie_zips = json.load(f)

pantry_map = pd.read_csv('map_data/PantryMap.csv')

def clean_zip(zipcode):
    try:
        return str(int(float(zipcode))).zfill(5)
    except:
        return None

pantry_map['Postal Code'] = pantry_map['Postal Code'].apply(clean_zip)
zip_counts = pantry_map['Postal Code'].value_counts().reset_index()
zip_counts.columns = ['ZCTA5CE10', 'count']

gdf = gpd.GeoDataFrame.from_features(erie_zips['features'])
gdf['ZCTA5CE10'] = gdf['ZCTA5CE10'].astype(str)
gdf = gdf.merge(zip_counts, on='ZCTA5CE10', how='left')
gdf['count'] = gdf['count'].fillna(0)

st.write(f"Data loaded: {len(gdf)} ZIP codes")

# Test 1: Standard Choropleth
st.header("Test 1: Standard Choropleth")
try:
    m1 = folium.Map(location=[42.8864, -78.8784], zoom_start=9)
    
    folium.Choropleth(
        geo_data=gdf.__geo_interface__,
        data=gdf,
        columns=['ZCTA5CE10', 'count'],
        key_on='feature.properties.ZCTA5CE10',
        fill_color='YlOrRd',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name='Count'
    ).add_to(m1)
    
    st.success("✅ Standard choropleth created")
    st_folium(m1, width=600, height=400)
except Exception as e:
    st.error(f"❌ Standard choropleth failed: {e}")

# Test 2: GeoJson with style function
st.header("Test 2: GeoJson with Style Function")
try:
    m2 = folium.Map(location=[42.8864, -78.8784], zoom_start=9)
    
    def style_function(feature):
        count = feature['properties']['count']
        if count > 10:
            return {'fillColor': 'red', 'color': 'black', 'weight': 1, 'fillOpacity': 0.7}
        elif count > 5:
            return {'fillColor': 'orange', 'color': 'black', 'weight': 1, 'fillOpacity': 0.7}
        elif count > 0:
            return {'fillColor': 'yellow', 'color': 'black', 'weight': 1, 'fillOpacity': 0.7}
        else:
            return {'fillColor': 'white', 'color': 'black', 'weight': 1, 'fillOpacity': 0.3}
    
    folium.GeoJson(
        gdf.__geo_interface__,
        style_function=style_function,
        tooltip=folium.GeoJsonTooltip(fields=['ZCTA5CE10', 'count'], aliases=['ZIP', 'Count'])
    ).add_to(m2)
    
    st.success("✅ GeoJson style function created")
    st_folium(m2, width=600, height=400)
except Exception as e:
    st.error(f"❌ GeoJson style function failed: {e}")

# Test 3: Individual polygons
st.header("Test 3: Individual Polygons")
try:
    m3 = folium.Map(location=[42.8864, -78.8784], zoom_start=9)
    
    for _, row in gdf.iterrows():
        if row['count'] > 0:
            color = 'red' if row['count'] > 10 else 'orange' if row['count'] > 5 else 'yellow'
            folium.GeoJson(
                row['geometry'],
                style_function=lambda x: {'fillColor': color, 'color': 'black', 'weight': 1, 'fillOpacity': 0.7},
                tooltip=f"ZIP: {row['ZCTA5CE10']}, Count: {int(row['count'])}"
            ).add_to(m3)
    
    st.success("✅ Individual polygons created")
    st_folium(m3, width=600, height=400)
except Exception as e:
    st.error(f"❌ Individual polygons failed: {e}")

st.write("---")
st.write("This tests different approaches to see which one works on Streamlit Cloud.") 