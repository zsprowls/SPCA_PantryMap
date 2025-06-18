import streamlit as st
import folium
from streamlit_folium import st_folium

st.title("CHOROPLETH ONLY TEST")
st.write("This should show ONLY a choropleth with two colored rectangles. NO PINS.")

# Create a very simple GeoJSON
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

st.write("Creating map...")

try:
    # Create map
    m = folium.Map(location=[42.85, -78.85], zoom_start=10)
    
    # Add ONLY choropleth
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
    
    st.success("✅ CHOROPLETH CREATED SUCCESSFULLY!")
    st.write("You should see two colored rectangles below:")
    st_folium(m, width=600, height=400)
    
except Exception as e:
    st.error(f"❌ CHOROPLETH FAILED: {e}")
    st.write(f"Error details: {str(e)}")

st.write("---")
st.write("If you see pins instead of colored rectangles, there's a routing issue.")
st.write("If you see an error, choropleths don't work on Streamlit Cloud.")
st.write("If you see colored rectangles, choropleths work and our data is the problem.") 