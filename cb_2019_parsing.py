import geopandas as gpd

# Load the shapefile (not just the .dbf)
gdf = gpd.read_file("cb_2019_us_tract_500k/cb_2019_us_tract_500k.shp")

# Preview the attribute data
print(gdf.head())

# Show available columns
print(gdf.columns)
print(f"Number of rows: {gdf.shape[0]}")
