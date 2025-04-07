import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
from geopy.geocoders import Nominatim

# Load shapefile of bureau tracts
tracts = gpd.read_file("/Users/michaelhayashi/development/hpy/geocode/tl_2024_25_tract/tl_2024_25_tract.shp")  # update with actual path

# Load persistent poverty tracts data
poverty_data = pd.read_csv("/Users/michaelhayashi/development/hpy/geocode/list-of-census-tracts-in-persistent-poverty.csv")  # assume CSV with columns: State, County, County ID, Tract

# Set up geocoder
geolocator = Nominatim(user_agent="poverty_check_ma")

def get_coordinates(address):
    try:
        location = geolocator.geocode(address)
        return (location.latitude, location.longitude) if location else (None, None)
    except Exception as e:
        # breakpoint()
        print("location not gettable", e)
        return (None, None)

def get_census_tract(lat, lon):
    point = Point(lon, lat)
    for _, tract in tracts.iterrows():
        if tract.geometry.contains(point):
            return tract['TRACTCE']  # Replace with the column that holds the tract FIPS code
    return None

# Read and process each address
with open('addresses.txt', 'r') as f:
    addresses = [line.strip() for line in f]

for address in addresses:
    lat, lon = get_coordinates(address)
    if lat is None or lon is None:
        print(f"Could not geocode: {address}")
        continue

    tract_code = get_census_tract(lat, lon)
    if tract_code is None:
        print(f"Tract not found for: {address}")
        continue

    if tract_code in poverty_data['Tract'].astype(str).values:
        print(f"{address} is in a persistent poverty tract.")
    else:
        print(f"{address} is NOT in a persistent poverty tract.")
