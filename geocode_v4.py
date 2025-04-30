import requests
import pandas as pd
import csv
import os

# === STEP 1: Load poverty GEOIDs (already full FIPS codes like '01001021100') ===
poverty_data = pd.read_csv(
    "list-of-census-tracts-in-persistent-poverty.csv",
    dtype={'Tract': str}
)
poverty_tracts = set(poverty_data['Tract'])

# === STEP 2: Read addresses from addresses.txt ===
with open("test.txt", "r") as f:
    lines = [line.strip() for line in f]

# === STEP 3: Write batch_input.csv (must be: ID, Street, City, State, ZIP) ===
input_file = "batch_input.csv"

with open(input_file, "w", newline="") as f:
    writer = csv.writer(f)
    for i, full_address in enumerate(lines):
        # Naive split assuming format: "777 Brockton Avenue, Abington, MA 2351"
        try:
            street, citystatezip = full_address.split(",", 1)
            city, statezip = citystatezip.strip().split(",", 1)
            state, zip = tuple(statezip.strip().split(" "))
            writer.writerow([i, street.strip(), city.strip(), state.strip(), zip.strip()])
        except Exception as e:
            print(f"⚠️ Could not parse address: {full_address} — {e}")

# === STEP 4: Send POST request to Census Batch Geocoder ===
with open(input_file, "rb") as f:
    files = {'addressFile': f}
    data = {
        'benchmark': 'Public_AR_Current',
        'vintage': 'Current_Current'
    }
    response = requests.post(
        "https://geocoding.geo.census.gov/geocoder/geographies/addressbatch",
        files=files,
        data=data
    )

# === STEP 5: Check response ===
# if not response.ok or not response.headers['Content-Type'].startswith("text/csv"):
if not response.ok:
    print("❌ Error: Received non-CSV response from Census API:")
    print(response.text)
    exit(1)

# === STEP 6: Parse results ===
results = csv.reader(response.text.splitlines())

print("\n--- Geocoding Results ---\n")
for row in results:
    if len(row) < 10:
        print(f"Incomplete or no match: {row}")
        continue

    index = row[0]
    input_address = lines[int(index)]
    geoid = row[9]  # Full GEOID

    # state_fips = geoid[:2]
    # county_fips = geoid[2:5]
    # tract_code = geoid[5:]

    # print(f"Address: {input_address}")
    # print(f"  GEOID: {geoid}")
    # print(f"  State FIPS: {state_fips}")
    # print(f"  County FIPS: {county_fips}")
    # print(f"  Census Tract: {tract_code}")

    if geoid in poverty_tracts:
        print(f"{input_address}  → This tract IS in a persistent poverty area.\n")
    else:
        print(f"{input_address}  → This tract is NOT in a persistent poverty area.\n")

# === Optional: Clean up the temp file ===
os.remove(input_file)
