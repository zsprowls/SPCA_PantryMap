import streamlit as st
import folium
from streamlit_folium import st_folium

st.title("CHOROPLETH ONLY TEST")
st.write("This should show ONLY a choropleth with two colored rectangles. NO PINS.")

# Create a very simple GeoJSON with better coordinates
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

st.write("GeoJSON created:")
st.json(simple_geojson)

st.write("Creating map...")

try:
    # Create map centered on the polygons
    m = folium.Map(location=[42.85, -78.85], zoom_start=12)
    
    # Add a simple marker to confirm map is working
    folium.Marker([42.85, -78.85], popup="Center").add_to(m)
    
    # Try choropleth with simpler parameters
    folium.Choropleth(
        geo_data=simple_geojson,
        name='Test Choropleth',
        fill_color='red',
        fill_opacity=0.8,
        line_opacity=1.0,
        legend_name='Test Values'
    ).add_to(m)
    
    st.success("✅ CHOROPLETH CREATED SUCCESSFULLY!")
    st.write("You should see two red rectangles and one marker below:")
    st_folium(m, width=600, height=400)
    
except Exception as e:
    st.error(f"❌ CHOROPLETH FAILED: {e}")
    st.write(f"Error details: {str(e)}")

st.write("---")
st.write("If you see a black box, the choropleth is trying to render but has issues.")
st.write("If you see red rectangles, choropleths work!")
st.write("If you see just a marker, the choropleth failed silently.") 