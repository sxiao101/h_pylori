import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
from geopy.geocoders import Nominatim
import time

def geocode_address(address):
    geolocator = Nominatim(user_agent="poverty_check_ma")
    location = geolocator.geocode(address)
    if location:
        return location.latitude, location.longitude
    else:
        return None, None

def load_ma_poverty_data(shapefile_path, csv_path):
    
    # Load ma tracts shapefile
    gdf = gpd.read_file(shapefile_path)

    # Load ACS poverty CSV
    poverty_df = pd.read_csv(csv_path, dtype=str)

    # Extract 11-digit GEOID from GEO_ID
    poverty_df["GEOID"] = poverty_df["GEO_ID"].str[-11:]

    # Filter to ma (FIPS starts with '25')
    poverty_df = poverty_df[poverty_df["GEOID"].str.startswith("25")].copy()

    # Use the poverty estimate percentage
    poverty_df["pct_below_poverty"] = pd.to_numeric(poverty_df["S1701_C03_001E"], errors="coerce")

    # Merge with shapefile on GEOID
    gdf["GEOID"] = gdf["GEOID"].astype(str)
    merged = gdf.merge(poverty_df[["GEOID", "pct_below_poverty"]], on="GEOID", how="left")

    return merged.dropna(subset=["pct_below_poverty"])

def is_high_poverty_area(lat, lon, poverty_gdf, threshold=20.0):
    point = Point(lon, lat)
    for _, row in poverty_gdf.iterrows():
        if row['geometry'].contains(point):
            return float(row['pct_below_poverty']) >= threshold
    return False

def process_addresses(address_file, shapefile_path, csv_path):
    poverty_gdf = load_ma_poverty_data(shapefile_path, csv_path)

    with open(address_file, "r") as f:
        addresses = [line.strip() for line in f if line.strip()]

    for address in addresses:
        try:
            lat, lon = geocode_address(address)
            if lat is None or lon is None:
                print(f"{address}: Geocoding failed.")
                continue

            in_poverty = is_high_poverty_area(lat, lon, poverty_gdf)
            status = "High poverty area" if in_poverty else "Not high poverty"
            print(f"{address}: {status}")
            time.sleep(1)  # avoid hitting geocoding rate limit
        except Exception as e:
            print(f"{address}: Error - {e}")

# Example usage
if __name__ == "__main__":
    shapefile_path = "/Users/michaelhayashi/development/hpy/geocode/tl_2024_25_tract/tl_2024_25_tract.shp"  # MA tracts shapefile
    csv_path = "/Users/michaelhayashi/development/hpy/geocode/ACSST1Y2023.S1701_2025-03-28T133111/ACSST1Y2023.S1701-Data.csv"                # National CSV                     # National ACS file
    address_file = "test_addresses.txt"                             # Your address list

    process_addresses(address_file, shapefile_path, csv_path)
