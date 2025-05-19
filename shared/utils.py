import os
import streamlit as st
import pandas as pd
import geopandas as gpd
import json
from shared.drive_utils import load_json_from_drive

# Constants
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SHARED_DATA_PATH = os.path.join(PROJECT_ROOT, 'shared_data')

# Authentication
def check_password():
    """Returns `True` if the user had the correct password."""
    def password_entered():
        if st.session_state["password"] == "SPCAMaps*":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        return True

# Data loading functions
@st.cache_data
def load_geojson():
    """Load the Erie County ZIP codes GeoJSON file from Google Drive."""
    try:
        geojson_data = load_json_from_drive('erie_survey_zips.geojson')
        gdf = gpd.GeoDataFrame.from_features(geojson_data['features'])
        gdf.set_crs(epsg=4326, inplace=True)  # Set CRS to WGS84
        return gdf
    except Exception as e:
        st.error(f"Error loading GeoJSON file: {str(e)}")
        st.stop()

# TODO: Add Google Drive integration functions here
def load_from_drive(file_id):
    """Load data from Google Drive using file ID."""
    # This will be implemented when we set up Google Drive integration
    pass 