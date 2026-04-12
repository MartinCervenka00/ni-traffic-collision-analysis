from pathlib import Path
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

# Create file paths
DATA_DIR = Path("data")
OUTPUT_DIR = Path("outputs")

# Uploading CSV RTC files - collision, casualty, vehicle
COLLISION_CSV = DATA_DIR / "collisions_2024.csv"
CASUALTY_CSV = DATA_DIR / "casualties_2024.csv"
VEHICLE_CSV = DATA_DIR / "vehicles_2024.csv"

# Load shapefiles - NI outline, NI districts
outline = gpd.read_file(DATA_DIR/"ni_outline.shp")
districts = gpd.read_file(DATA_DIR/"ni_districts.shp")

# Loading collision data from CSV into a pandas DataFrame
collisions = pd.read_csv(COLLISION_CSV)

print("Data loaded")

# Creating collision points (TM65 Irish Grid - EPSG = 29901, where a_gd1 = Easting and a_gd2 = Northing)
collisions_gdf = gpd.GeoDataFrame(
    collisions,
    geometry=gpd.points_from_xy(collisions["a_gd1"], collisions["a_gd2"]),
    crs="EPSG:29901"
)

# Match crs to collision data
outline = outline.to_crs(epsg=29901)
districts = districts.to_crs(epsg=29901)

# Area is being plotted for both ni outline, districts and collision
fig, ax = plt.subplots()
outline.plot(ax=ax, facecolor="none", edgecolor="black")
districts.plot(ax=ax, facecolor="none", edgecolor="blue")
collisions_gdf.plot(ax=ax, color="red", markersize=1)

# Adding legend to the map
import matplotlib.patches as mpatches

outline_patch = mpatches.Patch(edgecolor="black", facecolor="none", label="NI Outline")
district_patch = mpatches.Patch(edgecolor="blue", facecolor="none", label="Districts")
collision_patch = mpatches.Patch(color="red", label="Collisions")

ax.legend(handles=[outline_patch, district_patch, collision_patch])

plt.title("Road traffic collisions in Northern Ireland (2024)")
plt.show()
print("Map created")

# Creating spatial join - connect collisions to districts
joined = gpd.sjoin(collisions_gdf, districts, how="inner", predicate="within")

# Count collisions by district
by_district = joined.groupby("LGDNAME").size().sort_values(ascending=False)

# Create outputs folder if it doesn't exist
OUTPUT_DIR.mkdir(exist_ok=True)

# Save results to CSV file in the Output folder
by_district.to_csv(OUTPUT_DIR / "collisions_by_district.csv")

print("collisions_by_district.csv created")