import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
import pandas as pd
import json
import geopandas as gpd

# File IDs for your data files
FILE_IDS = {
    'erie_survey_zips': '1yIDEDCHHQadP716ffnnIDUmffe4WmZZE',
    'combined_survey_results': '1zy5O44osikX7HuOiH-VL7CCwEHMK0V4o',
    'processed_pantry_data': '1a1WURI5_o7DdkHlTz-giCpr-fux5bh5i',
    'geocoded_pantry_data': '1lDIHsWMjAJV7NOIW9K1qerfbWo2T5SE_',
    'pantry_map': '1RIzcas5Y2XyvDokqyZ-m8cIHPaa09gl-'
}

def get_drive_service():
    """Get an authenticated Google Drive service."""
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=['https://www.googleapis.com/auth/drive.readonly']
    )
    return build('drive', 'v3', credentials=credentials)

def download_file(file_id):
    """Download a file from Google Drive."""
    service = get_drive_service()
    request = service.files().get_media(fileId=file_id)
    file = io.BytesIO()
    downloader = MediaIoBaseDownload(file, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
    file.seek(0)
    return file

def load_csv(file_id):
    """Load a CSV file from Google Drive into a pandas DataFrame."""
    file = download_file(file_id)
    return pd.read_csv(file)

def load_json(file_id):
    """Load a JSON file from Google Drive."""
    file = download_file(file_id)
    return json.load(file)

def load_geojson(file_id):
    """Load a GeoJSON file from Google Drive into a GeoDataFrame."""
    file = download_file(file_id)
    return gpd.read_file(file)

# Convenience functions for your specific files
def load_erie_survey_zips():
    """Load the Erie survey ZIP codes GeoJSON file."""
    return load_geojson(FILE_IDS['erie_survey_zips'])

def load_combined_survey_results():
    """Load the combined survey results CSV file."""
    return load_csv(FILE_IDS['combined_survey_results'])

def load_processed_pantry_data():
    """Load the processed pantry data JSON file."""
    return load_json(FILE_IDS['processed_pantry_data'])

def load_geocoded_pantry_data():
    """Load the geocoded pantry data JSON file."""
    return load_json(FILE_IDS['geocoded_pantry_data'])

def load_pantry_map():
    """Load the pantry map CSV file."""
    return load_csv(FILE_IDS['pantry_map']) 