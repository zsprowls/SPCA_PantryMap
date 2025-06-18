import pandas as pd
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
import time
import os

# File paths
input_path = 'map_data/pantry_locations.csv'
output_path = 'map_data/geocoded_pantry_locations.csv'

# Read the CSV file
df = pd.read_csv(input_path)

# If output exists, load it to resume
if os.path.exists(output_path):
    geocoded_df = pd.read_csv(output_path)
    # Merge to keep any new columns
    df = df.merge(geocoded_df[['address', 'latitude', 'longitude']], on='address', how='left', suffixes=('', '_geo'))
    # Use existing geocoded values if present
    df['latitude'] = df['latitude'].combine_first(df['latitude_geo'])
    df['longitude'] = df['longitude'].combine_first(df['longitude_geo'])
    df = df.drop(columns=[c for c in df.columns if c.endswith('_geo')])
else:
    df['latitude'] = None
    df['longitude'] = None

# Initialize the geocoder
geolocator = Nominatim(user_agent="spca_maps", timeout=10)

# Function to geocode an address with retry logic
def geocode_address(address, max_retries=5):
    for attempt in range(max_retries):
        try:
            time.sleep(2)  # 2 seconds between requests
            location = geolocator.geocode(address)
            if location:
                return location.latitude, location.longitude
            return None, None
        except (GeocoderTimedOut, GeocoderUnavailable):
            if attempt == max_retries - 1:
                return None, None
            time.sleep(5)  # Wait longer between retries
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None, None

# Geocode each address, skipping those already done
for idx, row in df.iterrows():
    if pd.notnull(row['latitude']) and pd.notnull(row['longitude']):
        continue  # Already geocoded
    print(f"Geocoding {idx + 1}/{len(df)}: {row['name']}")
    lat, lon = geocode_address(row['address'])
    df.at[idx, 'latitude'] = lat
    df.at[idx, 'longitude'] = lon
    # Save progress after each geocode
    df.to_csv(output_path, index=False)

print(f"Geocoding complete! Results saved to {output_path}") 