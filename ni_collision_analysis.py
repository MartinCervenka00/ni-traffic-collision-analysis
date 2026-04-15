from pathlib import Path
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

# Create file paths
DATA_DIR = Path("data")
OUTPUT_DIR = Path("outputs")

# Select year for your analysis
YEAR = 2024

# Create function to create file paths for selected year
def get_year_file_paths(data_dir, year):
    """
    Create file paths for collision, casualty and vehicle data for a selected year.
    """
    collision_csv = data_dir / f"collisions_{year}.csv"
    casualty_csv = data_dir / f"casualties_{year}.csv"
    vehicle_csv = data_dir / f"vehicles_{year}.csv"

    return collision_csv, casualty_csv, vehicle_csv

# File paths for collision, casualty and vehicle data - for selected year
COLLISION_CSV, CASUALTY_CSV, VEHICLE_CSV = get_year_file_paths(DATA_DIR, YEAR)

# Creating function for saving total numbers of collisions, casualties and vehicles to the new line in each .csv
def save_with_total(series, output_path, column_name):
    """
    Saving collision, casualties and vehicle data per district to three new CSVs and add a total row at the end.
    """

    df = series.rename(column_name).reset_index()

    total_value = df[column_name].sum()

    total_row = pd.DataFrame({
        df.columns[0]: ["TOTAL"],
        column_name: [total_value]
    })

    df = pd.concat([df, total_row], ignore_index=True)

    df.to_csv(output_path, index=False)


# Load shapefiles - NI outline, NI districts
outline = gpd.read_file(DATA_DIR/"ni_outline.shp")
districts = gpd.read_file(DATA_DIR/"ni_districts.shp")

# Loading collision data from CSV into a pandas DataFrame
collisions = pd.read_csv(COLLISION_CSV)

print(f"Collision data loaded {YEAR}")

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

plt.title(f"Road traffic collisions in Northern Ireland ({YEAR})")

# Save image to output directory
OUTPUT_DIR.mkdir(exist_ok=True)
plt.savefig(OUTPUT_DIR / f"collisions_map_{YEAR}.png", dpi=300)

#remove a hashtag from the next line if you want to see the map and add # to the next line
#plt.show()
plt.close()

print(f"Map created {YEAR}")

# Creating spatial join - connect collisions to districts
joined = gpd.sjoin(collisions_gdf, districts, how="inner", predicate="within")

# Count collisions by district
by_district = joined.groupby("LGDNAME").size().sort_values(ascending=False)

# Create outputs folder if it doesn't exist
OUTPUT_DIR.mkdir(exist_ok=True)

# Save results to CSV file in the Output folder
save_with_total(
    by_district,
    OUTPUT_DIR / f"collisions_by_district_{YEAR}.csv",
    "collision_count"
)

print(f"Collisions_by_district_{YEAR}.csv created")

# Create graph for collisions in each district a save it to the Outputs folder as .png file
plt.figure(figsize=(10, 6))

by_district.sort_values().plot(kind="barh")
plt.title("Number of Collisions by District (2024)")
plt.xlabel("Collision Count")
plt.ylabel("District")
plt.grid(axis="x", linestyle="--", alpha=0.7)
plt.tight_layout()

plt.savefig(OUTPUT_DIR / f"collisions_by_districts_graph_{YEAR}.png", dpi=300)

plt.close()
print(f"Collision graph created {YEAR}")

# Next part will load casualties_2024.csv to the script
casualties = pd.read_csv(CASUALTY_CSV)

print(f"Casualties data loaded {YEAR}")

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
save_with_total(
    casualties_by_district,
    OUTPUT_DIR / f"casualties_by_district_{YEAR}.csv",
    "casualties_count"
)

print(f"Casualties_by_district_{YEAR}.csv created")

# Creating graph from casualties dataset
plt.figure(figsize=(10, 6))
casualties_by_district.sort_values().plot(kind="barh", color="green")
plt.title(f"Casualties by District ({YEAR})")
plt.xlabel("Number of casualties")
plt.ylabel("District")
plt.grid(axis="x", linestyle="--", alpha=0.7)
plt.tight_layout()

plt.savefig(OUTPUT_DIR / f"casualties_by_district_graph_{YEAR}.png", dpi=300)

plt.close()

print(f"Casualties graph created {YEAR}")

# Loading vehicles to the code (using Pandas library)
vehicles=pd.read_csv(VEHICLE_CSV)

print(f"Vehicles data loaded {YEAR}")

# Joining vehicles dataset with collisions data
collision_vehicle = collisions.merge(vehicles, on="a_ref", how="left")

# Using GeoPandas to convert vehicle data into spatial points using Easting and Northing from collision dataset
vehicles_gdf = gpd.GeoDataFrame(
    collision_vehicle,
    geometry=gpd.points_from_xy(collision_vehicle["a_gd1"], collision_vehicle["a_gd2"]),
    crs="EPSG:29901"
)

# Using spatial join with districts shapefile
joined_vehicles = gpd.sjoin(vehicles_gdf, districts, how="inner", predicate="within")

# Count vehicles by district
vehicles_by_district = joined_vehicles.groupby("LGDNAME").size().sort_values(ascending=False)

# Saving vehicle by district to new .csv file in Output folder
save_with_total(
    vehicles_by_district,
    OUTPUT_DIR / f"vehicles_by_district_{YEAR}.csv",
    "vehicles_count"
)

print(f"Vehicles_by_district_{YEAR}.csv created")

# Create third graph for dataset - vehicle by district
plt.figure(figsize=(10, 6))

vehicles_by_district.sort_values().plot(kind="barh", color="orange")
plt.title(f"Vehicles by District ({YEAR})")
plt.xlabel("Number of vehicles")
plt.ylabel("District")
plt.grid(axis="x", linestyle="--", alpha=0.7)
plt.tight_layout()

plt.savefig(OUTPUT_DIR / f"vehicles_by_district_graph_{YEAR}.png", dpi=300)

plt.close()

print(f"Vehicles graph created {YEAR}")