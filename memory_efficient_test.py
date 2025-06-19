import streamlit as st
import pandas as pd
import folium
import json
import geopandas as gpd
from streamlit_folium import st_folium

st.title("Memory-Efficient ZIP Code Visualization")

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

# Filter to only ZIP codes with data
gdf_with_data = gdf[gdf['count'] > 0].copy()

st.write(f"Total ZIP codes: {len(gdf)}")
st.write(f"ZIP codes with data: {len(gdf_with_data)}")

# Approach 1: Large colored circles at ZIP centers
st.header("Approach 1: Large Colored Circles")
try:
    m1 = folium.Map(location=[42.8864, -78.8784], zoom_start=9)
    
    for _, row in gdf_with_data.iterrows():
        center = row['geometry'].centroid
        
        # Color and size based on count
        if row['count'] > 10:
            color = 'red'
            radius = 3000
        elif row['count'] > 5:
            color = 'orange'
            radius = 2500
        else:
            color = 'yellow'
            radius = 2000
        
        folium.Circle(
            location=[center.y, center.x],
            radius=radius,
            color=color,
            fill=True,
            fill_opacity=0.6,
            popup=f"<b>ZIP: {row['ZCTA5CE10']}</b><br>Client Count: {int(row['count'])}",
            tooltip=f"ZIP {row['ZCTA5CE10']}: {int(row['count'])} clients"
        ).add_to(m1)
    
    st.success("✅ Large circles created")
    st_folium(m1, width=600, height=400)
except Exception as e:
    st.error(f"❌ Large circles failed: {e}")

# Approach 2: Simple rectangles instead of complex polygons
st.header("Approach 2: Simple Rectangles")
try:
    m2 = folium.Map(location=[42.8864, -78.8784], zoom_start=9)
    
    for _, row in gdf_with_data.iterrows():
        bounds = row['geometry'].bounds  # Get bounding box
        center = row['geometry'].centroid
        
        # Color based on count
        if row['count'] > 10:
            color = 'red'
        elif row['count'] > 5:
            color = 'orange'
        else:
            color = 'yellow'
        
        # Create a simple rectangle using the bounding box
        folium.Rectangle(
            bounds=[[bounds[1], bounds[0]], [bounds[3], bounds[2]]],
            color=color,
            fill=True,
            fill_opacity=0.6,
            popup=f"<b>ZIP: {row['ZCTA5CE10']}</b><br>Client Count: {int(row['count'])}",
            tooltip=f"ZIP {row['ZCTA5CE10']}: {int(row['count'])} clients"
        ).add_to(m2)
    
    st.success("✅ Simple rectangles created")
    st_folium(m2, width=600, height=400)
except Exception as e:
    st.error(f"❌ Simple rectangles failed: {e}")

# Approach 3: Heatmap-style visualization
st.header("Approach 3: Heatmap Style")
try:
    m3 = folium.Map(location=[42.8864, -78.8784], zoom_start=9)
    
    # Create heatmap data
    heatmap_data = []
    for _, row in gdf_with_data.iterrows():
        center = row['geometry'].centroid
        # Weight based on count
        weight = min(row['count'] * 2, 20)  # Cap at 20 for visibility
        heatmap_data.append([center.y, center.x, weight])
    
    from folium.plugins import HeatMap
    HeatMap(heatmap_data, radius=25, blur=15).add_to(m3)
    
    st.success("✅ Heatmap created")
    st_folium(m3, width=600, height=400)
except Exception as e:
    st.error(f"❌ Heatmap failed: {e}")

st.write("---")
st.write("These approaches use much less memory than choropleths.") 