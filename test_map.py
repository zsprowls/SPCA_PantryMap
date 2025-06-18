import streamlit as st
import folium
from streamlit_folium import st_folium

st.title("Simple Map Test")

# Test 1: Basic map
st.header("Test 1: Basic Map")
try:
    m1 = folium.Map(location=[42.8864, -78.8784], zoom_start=9)
    st_folium(m1, width=600, height=400)
    st.success("Basic map works!")
except Exception as e:
    st.error(f"Basic map failed: {e}")

# Test 2: Map with different tiles
st.header("Test 2: Map with OpenStreetMap")
try:
    m2 = folium.Map(location=[42.8864, -78.8784], zoom_start=9, tiles='OpenStreetMap')
    st_folium(m2, width=600, height=400)
    st.success("OpenStreetMap works!")
except Exception as e:
    st.error(f"OpenStreetMap failed: {e}")

# Test 3: Map with marker
st.header("Test 3: Map with Marker")
try:
    m3 = folium.Map(location=[42.8864, -78.8784], zoom_start=9)
    folium.Marker([42.8864, -78.8784], popup="Test").add_to(m3)
    st_folium(m3, width=600, height=400)
    st.success("Map with marker works!")
except Exception as e:
    st.error(f"Map with marker failed: {e}")

st.write("If all tests fail, there's a fundamental issue with folium/streamlit-folium in this environment.") 