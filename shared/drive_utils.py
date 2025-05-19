import os
import pandas as pd
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
import streamlit as st

# Constants
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
FOLDER_NAME = 'SPCAMaps'

def get_drive_service():
    """Initialize and return a Google Drive service."""
    try:
        # Check if credentials are in session state
        if 'drive_service' not in st.session_state:
            # Load credentials from secrets
            creds_dict = st.secrets["gcp_service_account"]
            creds = service_account.Credentials.from_service_account_info(
                creds_dict, scopes=SCOPES
            )
            
            # Build the service
            service = build('drive', 'v3', credentials=creds)
            st.session_state['drive_service'] = service
            
        return st.session_state['drive_service']
    except Exception as e:
        st.error(f"Error initializing Google Drive service: {str(e)}")
        st.stop()

def get_folder_id(service, folder_name=FOLDER_NAME):
    """Get the ID of the specified folder."""
    try:
        # Search for the folder
        results = service.files().list(
            q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'",
            spaces='drive',
            fields='files(id, name)'
        ).execute()
        
        items = results.get('files', [])
        
        if not items:
            st.error(f"Could not find folder: {folder_name}")
            st.stop()
            
        return items[0]['id']
    except Exception as e:
        st.error(f"Error finding folder: {str(e)}")
        st.stop()

def get_file_id(service, folder_id, file_name):
    """Get the ID of a specific file in the folder."""
    try:
        # Search for the file in the folder
        results = service.files().list(
            q=f"'{folder_id}' in parents and name='{file_name}'",
            spaces='drive',
            fields='files(id, name)'
        ).execute()
        
        items = results.get('files', [])
        
        if not items:
            st.error(f"Could not find file: {file_name}")
            st.stop()
            
        return items[0]['id']
    except Exception as e:
        st.error(f"Error finding file: {str(e)}")
        st.stop()

def download_file(service, file_id):
    """Download a file from Google Drive."""
    try:
        request = service.files().get_media(fileId=file_id)
        file = io.BytesIO()
        downloader = MediaIoBaseDownload(file, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        return file.getvalue()
    except Exception as e:
        st.error(f"Error downloading file: {str(e)}")
        st.stop()

def load_csv_from_drive(file_name):
    """Load a CSV file from Google Drive."""
    try:
        service = get_drive_service()
        folder_id = get_folder_id(service)
        file_id = get_file_id(service, folder_id, file_name)
        content = download_file(service, file_id)
        return pd.read_csv(io.BytesIO(content))
    except Exception as e:
        st.error(f"Error loading CSV from Drive: {str(e)}")
        st.stop()

def load_json_from_drive(file_name):
    """Load a JSON file from Google Drive."""
    try:
        service = get_drive_service()
        folder_id = get_folder_id(service)
        file_id = get_file_id(service, folder_id, file_name)
        content = download_file(service, file_id)
        return json.loads(content.decode('utf-8'))
    except Exception as e:
        st.error(f"Error loading JSON from Drive: {str(e)}")
        st.stop() 