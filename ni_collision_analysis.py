from pathlib import Path
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Create file paths
DATA_DIR = Path("data")
OUTPUT_DIR = Path("outputs")

# Select year for your analysis
YEAR = 2025

# Create function to create file paths for selected year
def get_year_file_paths(data_dir, year):
    """
    Create file paths for collision, casualty and vehicle data for a selected year.

    Parameters:
    - data_dir: folder where the data files are stored
    - year: year of the dataset to use

    Returns:
    - paths for collision, casualty and vehicle CSV files
    """
    collision_csv = data_dir / f"collision{year}.csv"
    casualty_csv = data_dir / f"casualty{year}.csv"
    vehicle_csv = data_dir / f"vehicle{year}.csv"

    return collision_csv, casualty_csv, vehicle_csv

# File paths for collision, casualty and vehicle data - for selected year
COLLISION_CSV, CASUALTY_CSV, VEHICLE_CSV = get_year_file_paths(DATA_DIR, YEAR)

# Creating function for saving total numbers of collisions, casualties and vehicles to the new line in each .csv
def save_with_total(series, output_path, column_name):
    """
    Save district totals to a CSV file and add a final row showing the overall total.

    Parameters:
    - series: grouped results such as collisions, casualties or vehicles by district
    - output_path: location where the CSV file will be saved
    - column_name: name of the results column in the CSV file

    Returns:
    - saves a new CSV file with a TOTAL row at the end
    """

    df = series.rename(column_name).reset_index()

    total_value = df[column_name].sum()

    total_row = pd.DataFrame({
        df.columns[0]: ["TOTAL"],
        column_name: [total_value]
    })

    df = pd.concat([df, total_row], ignore_index=True)

    df.to_csv(output_path, index=False)

# Creating a Choropleth map using fatal collisions percentage per district
def create_choropleth_map(districts, severity_table, outline, output_dir, year,
                          column_name, legend_label, map_title, output_filename, cmap):
    """
    Create a choropleth map showing the percentage of fatal collisions by district.

    Parameters:
    - districts: GeoDataFrame of district boundaries
    - severity_table: table containing severity statistics by district
    - outline: GeoDataFrame of Northern Ireland outline
    - output_dir: folder where the output image will be saved
    - year: selected year for analysis

    Returns:
    - saves a PNG map in the outputs folder
    """

    # Join severity values to district boundaries
    districts_metric = districts.merge(
        severity_table.reset_index(),
        on="LGDNAME",
        how="left"
    )

    # Make sure layers use the same CRS
    districts_metric = districts_metric.to_crs(epsg=29901)
    outline = outline.to_crs(epsg=29901)

    # Create figure and axis
    fig, ax = plt.subplots(figsize=(10, 10))

    # Plot districts using percentage
    districts_metric.plot(
        column=column_name,
        cmap=cmap,
        linewidth=0.8,
        edgecolor="black",
        legend=True,
        legend_kwds={
            "label": legend_label,
            "shrink": 0.7
        },
        ax=ax,
        missing_kwds={
            "color": "lightgrey",
            "label": "No data"
        }
    )

    # Plot NI outline on top
    outline.boundary.plot(ax=ax, color="black", linewidth=1)

    # Add North arrow
    ax.annotate(
        'N',
        xy=(0.92, 0.92),
        xytext=(0.92, 0.85),
        arrowprops=dict(facecolor='black', width=2, headwidth=8),
        ha='center',
        va='center',
        fontsize=10,
        xycoords=ax.transAxes
    )

    # Add title and axis styling
    ax.set_title(f"{map_title} ({YEAR})")
    ax.tick_params(axis="both", labelsize=8)

    # Add dashed grid
    plt.grid(axis="both", linestyle="--", alpha=0.4)

    # Add source
    plt.figtext(
        0.1, 0.02,
        "Source: PSNI Road Traffic Collision Statistics, Open Data NI; OSNI Boundaries",
        fontsize=8
    )

    # Save map
    plt.tight_layout()
    plt.savefig(
        output_dir / output_filename, dpi=300)

    plt.close()

def create_district_table(joined_data, output_dir, year, output_name, column_name):
    """
    Create a district summary table from joined spatial data and save it as a CSV file.

    Parameters:
    - joined_data: GeoDataFrame after spatial join
    - output_dir: folder where the CSV file will be saved
    - year: selected year for analysis
    - output_name: short name for the output file
    - column_name: name of the results column in the CSV file

    Returns:
    - grouped district table
    """

    district_table = joined_data.groupby("LGDNAME").size().sort_values(ascending=False)

    save_with_total(
        district_table,
        output_dir / f"{year}_TABLE_{output_name}.csv",
        column_name
    )

    print(f"{year} TABLE {output_name}.csv created")

    return district_table

# Load shapefiles - NI outline, NI districts
outline = gpd.read_file(DATA_DIR/"ni_outline.shp")
districts = gpd.read_file(DATA_DIR/"ni_districts.shp")

# Loading collision data from CSV into a pandas DataFrame
collisions = pd.read_csv(COLLISION_CSV)

print(f"{YEAR} DATA Collision loaded")

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
fig, ax = plt.subplots(figsize=(10, 10))
outline.plot(ax=ax, facecolor="none", edgecolor="black")
districts.plot(ax=ax, facecolor="none", edgecolor="blue")
collisions_gdf.plot(ax=ax, color="red", markersize=1)

# Adding legend to the map

outline_patch = mpatches.Patch(edgecolor="black", facecolor="none", label="NI Outline")
district_patch = mpatches.Patch(edgecolor="blue", facecolor="none", label="Districts")
collision_patch = mpatches.Patch(color="red", label="Collisions")

ax.legend(handles=[outline_patch, district_patch, collision_patch],
          loc="upper left",
          bbox_to_anchor=(0.01, 0.99)
)
# Make coordinate numbers smaller
ax.tick_params(axis="both", labelsize=8)

# Add North arrow
ax.annotate(
    'N',
    xy=(0.92, 0.92),
    xytext=(0.92, 0.85),
    arrowprops=dict(facecolor='black', width=2, headwidth=8),
    ha='center',
    va='center',
    fontsize=10,
    xycoords=ax.transAxes
)

# Add source
plt.figtext(
    0.1, 0.02,
    "Source: PSNI Road Traffic Collision Statistics, Open Data NI; OSNI Boundaries",
    fontsize=8
)

plt.title(f" Total road traffic collisions in Northern Ireland ({YEAR})")

# Save image to output directory
OUTPUT_DIR.mkdir(exist_ok=True)
plt.savefig(OUTPUT_DIR / f"{YEAR}_MAP_collisions.png", dpi=300)

#remove a hashtag from the next line if you want to see the map and add # to the next line
#plt.show()
plt.close()

print(f"{YEAR} MAP total collisions in NI created")

# Creating spatial join - connect collisions to districts
joined = gpd.sjoin(collisions_gdf, districts, how="inner", predicate="within")

# Calling count collisions by district
by_district = create_district_table(
    joined,
    OUTPUT_DIR,
    YEAR,
    "collisions_by_district",
    "collision_count"
)

# Create graph for collisions in each district a save it to the Outputs folder as .png file
plt.figure(figsize=(10, 6))

by_district.sort_values().plot(kind="barh")
plt.title(f"Number of Collisions by District ({YEAR})")
plt.xlabel("Collision Count")
plt.ylabel("District")
plt.grid(axis="x", linestyle="--", alpha=0.7)
plt.tight_layout()

plt.savefig(OUTPUT_DIR / f"{YEAR}_GRAPH_collisions_by_districts.png", dpi=300)

plt.close()
print(f"{YEAR} GRAPH Collisions created")

# Next part will load casualties_2024.csv to the script
casualties = pd.read_csv(CASUALTY_CSV)

print(f"{YEAR} DATA Casualties loaded")

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

# Calling count casualties by district
casualties_by_district = create_district_table(
    joined_casualties,
    OUTPUT_DIR,
    YEAR,
    "casualties_by_district",
    "casualties_count"
)

# Creating graph from casualties dataset
plt.figure(figsize=(10, 6))
casualties_by_district.sort_values().plot(kind="barh", color="green")
plt.title(f"Casualties by District ({YEAR})")
plt.xlabel("Number of casualties")
plt.ylabel("District")
plt.grid(axis="x", linestyle="--", alpha=0.7)
plt.tight_layout()

plt.savefig(OUTPUT_DIR / f"{YEAR}_GRAPH_casualties_by_district.png", dpi=300)

plt.close()

print(f"{YEAR} GRAPH Casualties created")

# Loading vehicles to the code (using Pandas library)
vehicles=pd.read_csv(VEHICLE_CSV)

print(f"{YEAR} DATA Vehicles loaded")

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

# Calling count vehicles by district
vehicles_by_district = create_district_table(
    joined_vehicles,
    OUTPUT_DIR,
    YEAR,
    "vehicles_by_district",
    "vehicles_count"
)

# Create third graph for dataset - vehicle by district
plt.figure(figsize=(10, 6))

vehicles_by_district.sort_values().plot(kind="barh", color="orange")
plt.title(f"Vehicles by District ({YEAR})")
plt.xlabel("Number of vehicles")
plt.ylabel("District")
plt.grid(axis="x", linestyle="--", alpha=0.7)
plt.tight_layout()

plt.savefig(OUTPUT_DIR / f"{YEAR}_GRAPH_vehicles_by_district.png", dpi=300)

plt.close()

print(f"{YEAR} GRAPH Vehicles created ")

# Collision Severity Analysis

# Table with districts and columns with severity types
severity_table = (
    joined.groupby(["LGDNAME", "a_type"])
    .size()
    .unstack(fill_value=0)
)

# Rename the severity columns
severity_table = severity_table.rename(columns={
    1: "fatal",
    2: "serious",
    3: "slight"
})

# If one category is missing
for col in ["fatal", "serious", "slight"]:
    if col not in severity_table.columns:
        severity_table[col] = 0

# Add total collisions
severity_table["total"] = (
    severity_table["fatal"] +
    severity_table["serious"] +
    severity_table["slight"]
)

# calculate percentages
severity_table["fatal_percentage"] = (severity_table["fatal"] / severity_table["total"] * 100).round(2)
severity_table["serious_percentage"] = (severity_table["serious"] / severity_table["total"] * 100).round(2)
severity_table["slight_percentage"] = (severity_table["slight"] / severity_table["total"] * 100).round(2)

# calculate ratio (avoid division by zero)
severity_table["serious_to_slight_ratio"] = (severity_table["serious"] / severity_table["slight"].replace(0, pd.NA)
                                             ).round(3)

# save to csv
severity_table.to_csv(OUTPUT_DIR / f"{YEAR}_TABLE_severity_by_district.csv")
print(f"{YEAR} TABLE Severity_by_district.csv created")

# create bar chart - Collision Severity by District
severity_table[["fatal", "serious", "slight"]].plot(
    kind="bar",
    stacked=True,
    figsize=(14, 8),
    color=["red", "orange", "gold"],
    edgecolor="black",
    linewidth=0.8,
    width=0.9
)

plt.title(f"Collision Severity by District ({YEAR})")
plt.xlabel("District")
plt.ylabel("Number of collisions")
plt.legend(title="Severity")
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / f"{YEAR}_GRAPH_severity_by_district.png", dpi=300)
plt.close()

print(f"{YEAR} GRAPH Severity by district created")

# Fatal percentage choropleth
create_choropleth_map(
    districts,
    severity_table,
    outline,
    OUTPUT_DIR,
    YEAR,
    "fatal_percentage",
    "Fatal collisions (%)",
    "Percentage of Fatal Collisions by District",
    f"{YEAR}_MAP_fatal_percentage_choropleth.png",
    "Reds"
)
print(f"{YEAR} MAP fatal_percentage_choropleth created")

# Serious percentage choropleth
create_choropleth_map(
    districts,
    severity_table,
    outline,
    OUTPUT_DIR,
    YEAR,
    "serious_percentage",
    "Serious collisions (%)",
    "Percentage of Serious Collisions by District",
    f"{YEAR}_MAP_serious_percentage_choropleth.png",
    "Oranges"
)
print(f"{YEAR} MAP serious_percentage_choropleth created")

# Slight percentage choropleth
create_choropleth_map(
    districts,
    severity_table,
    outline,
    OUTPUT_DIR,
    YEAR,
    "slight_percentage",
    "Slight collisions (%)",
    "Percentage of Slight Collisions by District",
    f"{YEAR}_MAP_slight_percentage_choropleth.png",
    "YlGn"
)
print(f"{YEAR} MAP slight_percentage_choropleth created")

# Serious-to-slight ratio choropleth
create_choropleth_map(
    districts,
    severity_table,
    outline,
    OUTPUT_DIR,
    YEAR,
    "serious_to_slight_ratio",
    "Serious to slight ratio",
    "Serious-to-Slight Collision Ratio by District",
    f"{YEAR}_MAP_serious_to_slight_ratio_choropleth.png",
    "Purples"
)
print(f"{YEAR} MAP serious_to_slight_ratio_choropleth created")

# Use this to see text for docstring
# change the name of the function
#print(create_choropleth_map.__doc__)
