import requests
import pandas as pd

# Load persistent poverty tracts data (assumes you saved it as CSV)
poverty_data = pd.read_csv("/Users/michaelhayashi/development/hpy/geocode/list-of-census-tracts-in-persistent-poverty.csv", dtype={'Tract': str})
poverty_tracts = set(poverty_data['Tract'])

# Function to get census tract GEOID from address
import requests

def census_geocode(address):
    url = "https://geocoding.geo.census.gov/geocoder/geographies/onelineaddress"
    params = {
        "address": address,
        "benchmark": "Public_AR_Current",
        "vintage": "Current_Current",
        "format": "json"
    }

    try:
        response = requests.get(url, params=params, timeout=10)  # Timeout set to 10 seconds
        response.raise_for_status()  # Raise error for bad status codes (e.g., 400, 500)

        data = response.json()
        match = data["result"]["addressMatches"][0]
        geoid = match["geographies"]["Census Tracts"][0]["GEOID"]
        return geoid

    except requests.exceptions.Timeout:
        print(f"Timeout while geocoding: {address}")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error for address '{address}': {e}")
        return None
    except (IndexError, KeyError):
        print(f"No tract match found for address: {address}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Request error for address '{address}': {e}")
        return None


# Read addresses from file
with open("addresses.txt", "r") as f:
    addresses = [line.strip() for line in f]

# Process each address
for address in addresses:
    tract_id = census_geocode(address)
    if tract_id is None:
        print(f"Could not find tract for: {address}")
    elif tract_id in poverty_tracts:
        print(f"{address} → {tract_id} is in a persistent poverty tract.")
    else:
        print(f"{address} → {tract_id} is NOT in a persistent poverty tract.")
