import streamlit as st
import folium
from streamlit_folium import st_folium
import json

st.title("Simple Choropleth Test")

# Create a very simple GeoJSON for testing
simple_geojson = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {"name": "Area 1", "value": 10},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [-78.9, 42.8],
                    [-78.8, 42.8],
                    [-78.8, 42.9],
                    [-78.9, 42.9],
                    [-78.9, 42.8]
                ]]
            }
        },
        {
            "type": "Feature",
            "properties": {"name": "Area 2", "value": 20},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [-78.8, 42.8],
                    [-78.7, 42.8],
                    [-78.7, 42.9],
                    [-78.8, 42.9],
                    [-78.8, 42.8]
                ]]
            }
        }
    ]
}

st.write("Testing with a simple GeoJSON...")

try:
    # Create a simple map
    m = folium.Map(location=[42.85, -78.85], zoom_start=10)
    
    # Try to add a simple choropleth
    folium.Choropleth(
        geo_data=simple_geojson,
        data=None,
        columns=None,
        key_on='feature.properties.name',
        fill_color='YlOrRd',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name='Test Values'
    ).add_to(m)
    
    st.success("✅ Simple choropleth created!")
    st_folium(m, width=600, height=400)
    
except Exception as e:
    st.error(f"❌ Simple choropleth failed: {e}")
    st.write(f"Error type: {type(e)}")
    st.write(f"Error details: {str(e)}")

st.write("---")
st.write("If this works, the issue is with our specific GeoJSON data. If this fails, there's a fundamental issue with folium choropleths on Streamlit Cloud.") 