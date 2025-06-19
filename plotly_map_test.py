import streamlit as st
import plotly.express as px
import pandas as pd
import json

st.title("Plotly Map Test")

# Create some test data
test_data = pd.DataFrame({
    'lat': [42.8864, 42.9, 42.87],
    'lon': [-78.8784, -78.85, -78.9],
    'name': ['Test 1', 'Test 2', 'Test 3'],
    'size': [10, 15, 20]
})

st.header("Test 1: Basic Plotly Scatter Mapbox")
try:
    fig = px.scatter_mapbox(
        test_data,
        lat='lat',
        lon='lon',
        hover_name='name',
        size='size',
        color='size',
        zoom=9,
        center={'lat': 42.8864, 'lon': -78.8784},
        mapbox_style='open-street-map'
    )
    fig.update_layout(margin={'r': 0, 't': 0, 'l': 0, 'b': 0})
    st.plotly_chart(fig, use_container_width=True)
    st.success("✅ Plotly scatter mapbox works!")
except Exception as e:
    st.error(f"❌ Plotly scatter mapbox failed: {e}")

st.header("Test 2: Plotly with CartoDB tiles")
try:
    fig2 = px.scatter_mapbox(
        test_data,
        lat='lat',
        lon='lon',
        hover_name='name',
        size='size',
        color='size',
        zoom=9,
        center={'lat': 42.8864, 'lon': -78.8784},
        mapbox_style='carto-positron'
    )
    fig2.update_layout(margin={'r': 0, 't': 0, 'l': 0, 'b': 0})
    st.plotly_chart(fig2, use_container_width=True)
    st.success("✅ Plotly with CartoDB tiles works!")
except Exception as e:
    st.error(f"❌ Plotly with CartoDB tiles failed: {e}")

st.header("Test 3: Plotly with Stamen tiles")
try:
    fig3 = px.scatter_mapbox(
        test_data,
        lat='lat',
        lon='lon',
        hover_name='name',
        size='size',
        color='size',
        zoom=9,
        center={'lat': 42.8864, 'lon': -78.8784},
        mapbox_style='stamen-terrain'
    )
    fig3.update_layout(margin={'r': 0, 't': 0, 'l': 0, 'b': 0})
    st.plotly_chart(fig3, use_container_width=True)
    st.success("✅ Plotly with Stamen tiles works!")
except Exception as e:
    st.error(f"❌ Plotly with Stamen tiles failed: {e}")

st.write("---")
st.write("If Plotly works but folium doesn't, we should switch to Plotly for the main app.") 