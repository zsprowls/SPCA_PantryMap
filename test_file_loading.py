import streamlit as st
from drive_utils import (
    load_erie_survey_zips,
    load_combined_survey_results,
    load_processed_pantry_data,
    load_geocoded_pantry_data,
    load_pantry_map
)

def test_file_loading():
    try:
        print("Testing file loading...")
        
        # Test loading Erie survey ZIPs
        print("\nLoading Erie survey ZIPs...")
        erie_zips = load_erie_survey_zips()
        print(f"Successfully loaded Erie survey ZIPs. Shape: {erie_zips.shape}")
        
        # Test loading combined survey results
        print("\nLoading combined survey results...")
        survey_results = load_combined_survey_results()
        print(f"Successfully loaded survey results. Shape: {survey_results.shape}")
        
        # Test loading processed pantry data
        print("\nLoading processed pantry data...")
        pantry_data = load_processed_pantry_data()
        print(f"Successfully loaded processed pantry data. Type: {type(pantry_data)}")
        
        # Test loading geocoded pantry data
        print("\nLoading geocoded pantry data...")
        geocoded_data = load_geocoded_pantry_data()
        print(f"Successfully loaded geocoded pantry data. Type: {type(geocoded_data)}")
        
        # Test loading pantry map
        print("\nLoading pantry map...")
        pantry_map = load_pantry_map()
        print(f"Successfully loaded pantry map. Shape: {pantry_map.shape}")
        
        print("\nAll files loaded successfully!")
        return True
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_file_loading() 