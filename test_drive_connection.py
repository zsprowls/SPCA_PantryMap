import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

def get_folder_id(service, folder_name):
    """Get the ID of a folder by its name."""
    results = service.files().list(
        q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false",
        fields="files(id, name)"
    ).execute()
    items = results.get('files', [])
    if items:
        return items[0]['id']
    return None

def list_files_in_folder(service, folder_id):
    """List all files in a specific folder."""
    results = service.files().list(
        q=f"'{folder_id}' in parents and trashed=false",
        fields="files(id, name, mimeType)"
    ).execute()
    return results.get('files', [])

def download_file(service, file_id):
    """Download a file's content."""
    request = service.files().get_media(fileId=file_id)
    file = io.BytesIO()
    downloader = MediaIoBaseDownload(file, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
    file.seek(0)
    return file

def test_drive_connection():
    try:
        # Load credentials from Streamlit secrets
        credentials = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=['https://www.googleapis.com/auth/drive.readonly']
        )
        
        # Build the Drive API service
        service = build('drive', 'v3', credentials=credentials)
        
        # Get the SPCAMaps folder ID
        folder_name = "SPCAMaps"
        folder_id = get_folder_id(service, folder_name)
        
        if folder_id:
            print(f"Found folder '{folder_name}' with ID: {folder_id}")
            
            # List files in the folder
            files = list_files_in_folder(service, folder_id)
            
            if not files:
                print(f'No files found in {folder_name}.')
            else:
                print(f'\nFiles in {folder_name}:')
                for file in files:
                    print(f"- {file['name']} (ID: {file['id']}, Type: {file['mimeType']})")
                    
                    # If it's a file (not a folder), demonstrate how to download it
                    if file['mimeType'] != 'application/vnd.google-apps.folder':
                        print(f"  Can be downloaded using file ID: {file['id']}")
        else:
            print(f"Folder '{folder_name}' not found.")
                
        return True
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_drive_connection() 