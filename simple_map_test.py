import streamlit as st
import folium
from streamlit_folium import st_folium

st.title("Simple Map Test")

# Test 1: Basic map with no data
st.header("Test 1: Basic Map")
try:
    m1 = folium.Map(location=[42.8864, -78.8784], zoom_start=9)
    st_folium(m1, width=600, height=400)
    st.success("✅ Basic map works!")
except Exception as e:
    st.error(f"❌ Basic map failed: {e}")

# Test 2: Map with one marker
st.header("Test 2: Map with One Marker")
try:
    m2 = folium.Map(location=[42.8864, -78.8784], zoom_start=9)
    folium.Marker([42.8864, -78.8784], popup="Test").add_to(m2)
    st_folium(m2, width=600, height=400)
    st.success("✅ Map with marker works!")
except Exception as e:
    st.error(f"❌ Map with marker failed: {e}")

# Test 3: Map with one circle
st.header("Test 3: Map with One Circle")
try:
    m3 = folium.Map(location=[42.8864, -78.8784], zoom_start=9)
    folium.Circle(
        location=[42.8864, -78.8784],
        radius=1000,
        color='red',
        fill=True,
        fill_opacity=0.6
    ).add_to(m3)
    st_folium(m3, width=600, height=400)
    st.success("✅ Map with circle works!")
except Exception as e:
    st.error(f"❌ Map with circle failed: {e}")

# Test 4: Map with marker cluster
st.header("Test 4: Map with Marker Cluster")
try:
    from folium.plugins import MarkerCluster
    m4 = folium.Map(location=[42.8864, -78.8784], zoom_start=9)
    marker_cluster = MarkerCluster().add_to(m4)
    folium.Marker([42.8864, -78.8784], popup="Test").add_to(marker_cluster)
    st_folium(m4, width=600, height=400)
    st.success("✅ Map with marker cluster works!")
except Exception as e:
    st.error(f"❌ Map with marker cluster failed: {e}")

st.write("---")
st.write("If all tests fail, there's a fundamental issue with folium on Streamlit Cloud.")
st.write("If some tests work, we can identify what specific feature is causing the problem.") 