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

print("Collision data loaded")

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

# Save image to output directory
OUTPUT_DIR.mkdir(exist_ok=True)
plt.savefig(OUTPUT_DIR / "collisions_map.png", dpi=300)

#remove a hashtag from the next line if you want to see the map and add # to the next line
#plt.show()
plt.close()

print("Map created")

# Creating spatial join - connect collisions to districts
joined = gpd.sjoin(collisions_gdf, districts, how="inner", predicate="within")

# Count collisions by district
by_district = joined.groupby("LGDNAME").size().sort_values(ascending=False)

# Create outputs folder if it doesn't exist
OUTPUT_DIR.mkdir(exist_ok=True)

# Save results to CSV file in the Output folder
by_district.rename("collision_count").to_csv(
    OUTPUT_DIR / "collisions_by_district.csv"
)

print("Collisions_by_district.csv created")

# Create graph for collisions in each district a save it to the Outputs folder as .png file
plt.figure(figsize=(10, 6))

by_district.sort_values().plot(kind="barh")

plt.title("Number of Collisions by District (2024)")
plt.xlabel("Collision Count")
plt.ylabel("District")

plt.grid(axis="x", linestyle="--", alpha=0.7)

plt.tight_layout()

OUTPUT_DIR.mkdir(exist_ok=True)
plt.savefig(OUTPUT_DIR / "collisions_graph.png", dpi=300)

plt.close()
print("Collision graph created")

# Next part will load casualties_2024.csv to the script
casualties = pd.read_csv(CASUALTY_CSV)

print("Casualties data loaded")

# Casualties will be joined with collisions data
collision_casualty = collisions.merge(casualties, on="a_ref", how="left")

# Dataset is converted into a GeoDataFrame using Easting and Northing from collision
casualties_gdf = gpd.GeoDataFrame(
    collision_casualty,
    geometry=gpd.points_from_xy(collision_casualty["a_gd1"], collision_casualty["a_gd2"]),
    crs="EPSG:29901"
)

# Use spatial join to districts boundaries
joined_casualties = gpd.sjoin(casualties_gdf, districts, how="inner", predicate="within")

# Count casualties by district
casualties_by_district = joined_casualties.groupby("LGDNAME").size().sort_values(ascending=False)

# Saving new data from casualties to .csv file into Output folder
casualties_by_district.rename("casualty_count").to_csv(
    OUTPUT_DIR / "casualties_by_district.csv"
)

print("Casualties_by_district.csv created")

# Creating graph from casualties dataset
plt.figure(figsize=(10, 6))
casualties_by_district.sort_values().plot(kind="barh", color="green")
plt.title("Casualties by District (2024)")
plt.xlabel("Number of casualties")
plt.ylabel("District")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "casualties_by_district.png", dpi=300)

plt.close()

print("Casualties graph created")

# Loading vehicles to the code (using Pandas library)
vehicles=pd.read_csv(VEHICLE_CSV)

print("Vehicles data loaded")

# Joining vehicles dataset with collisions data
collision_vehicle = collisions.merge(vehicles, on="a_ref", how="left")