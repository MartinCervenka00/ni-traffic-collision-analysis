from pathlib import Path
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Select year for your analysis
YEAR = 2025

# Create file paths and ensure the outputs folder exists
DATA_DIR = Path("data")
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

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

# Creating function to add north arrow, scale bar and source text to maps
def add_map_elements(ax,
                     source_text="Source: PSNI Road Traffic Collision Statistics, Open Data NI; OSNI Boundaries",
                     scale_length=20000):

    """
    Add north arrow, source text and scale bar to a map.

    Parameters:
    - ax: matplotlib axis
    - source_text: text shown at bottom of figure
    - scale_length: scale bar length in metres (EPSG:29901 uses metres)

    Returns:
    - None. Adds map elements directly to the matplotlib axis (add_map_elements(ax))
    """

    # North arrow
    ax.annotate(
        "N",
        xy=(0.93, 0.93),
        xytext=(0.93, 0.85),
        arrowprops=dict(
            facecolor="black",
            width=2,
            headwidth=8
        ),
        ha="center",
        va="center",
        fontsize=10,
        xycoords=ax.transAxes
    )

    # Scale bar
    xmin, xmax = ax.get_xlim()
    ymin, ymax = ax.get_ylim()

    x_start = xmin + (xmax - xmin) * 0.05
    y_start = ymin + (ymax - ymin) * 0.05

    # Main scale line
    ax.plot(
        [x_start, x_start + scale_length],
        [y_start, y_start],
        color="black",
        linewidth=2
    )

    # End ticks
    ax.plot(
        [x_start, x_start],
        [y_start - 500, y_start + 500],
        color="black",
        linewidth=2
    )

    ax.plot(
        [x_start + scale_length, x_start + scale_length],
        [y_start - 500, y_start + 500],
        color="black",
        linewidth=2
    )

    # Scale text
    ax.text(
        x_start + scale_length / 2,
        y_start + 1200,
        f"{int(scale_length / 1000)} km",
        ha="center",
        fontsize=9
    )

    # Source text
    plt.figtext(0.10,0.02,source_text,fontsize=8)

## Adding boundary legend to the hotspot and choropleth maps
def add_boundary_legend(ax, outline_label="NI Outline", district_label="District Boundaries"):
    """
    Add a boundary legend showing the NI outline and district boundaries.

    Parameters:
    - ax: matplotlib axis
    - outline_label: label for the Northern Ireland outline
    - district_label: label for district boundaries

     Returns:
    - None. Adds the legend directly to the matplotlib axis.

    """

    outline_patch = mpatches.Patch(edgecolor="black",facecolor="none",label=outline_label)
    district_patch = mpatches.Patch(edgecolor="grey",facecolor="none",linewidth=0.5,label=district_label)
    ax.legend(handles=[outline_patch, district_patch],loc="upper left")

# Creating a Choropleth map using fatal collisions percentage per district
def create_choropleth_map(districts, severity_table, outline, output_dir, year,
                          column_name, legend_label, map_title, formula_text, output_filename, cmap):

    """
    Create a choropleth map showing a selected collision severity metric by district.

    Parameters:
    - districts: GeoDataFrame of district boundaries
    - severity_table: table containing severity statistics by district
    - outline: GeoDataFrame of Northern Ireland outline
    - output_dir: folder where the output image will be saved
    - year: selected year for analysis
    - column_name: name of the data column to map
    - legend_label: label shown on the colour legend
    - map_title: main title of the map
    - formula_text: formula shown below the title
    - output_filename: name of the PNG output file
    - cmap: colour map used for shading districts

    Returns:
    - saves a PNG map in the outputs folder
    """

    # Join severity values to district boundaries
    districts_metric = districts.merge(severity_table.reset_index(),on="LGDNAME",how="left")

    # Make sure layers use the same CRS
    districts_metric = districts_metric.to_crs(epsg=29901)
    outline = outline.to_crs(epsg=29901)

    # Create figure and axis
    fig, ax = plt.subplots(figsize=(9, 6.5))

    # Plot districts using percentage
    districts_metric.plot(column=column_name,cmap=cmap,linewidth=0.4,edgecolor="black",legend=True,
                          legend_kwds={"label": legend_label,"shrink": 0.7},
                          ax=ax,missing_kwds={"color": "lightgrey","label": "No data"})

    # Plot NI outline on top
    outline.boundary.plot(ax=ax, color="black", linewidth=1)

    # Add boundary legend
    add_boundary_legend(ax)

    # Main title
    ax.set_title(f"{map_title} ({year})", fontsize=12, pad=16)

    # Second title with formula
    ax.text(0.5, 1.01, formula_text, transform=ax.transAxes, ha="center", va="bottom", fontsize=9)

    # Axis styling
    ax.tick_params(axis="both", labelsize=8)

    # Add dashed grid
    plt.grid(axis="both", linestyle="--", alpha=0.4)

    # Add north arrow, source, scale
    add_map_elements(ax)

    # Save map
    plt.tight_layout(rect=[0.02,0.04, 0.98, 0.95])
    plt.savefig(output_dir / output_filename, dpi=300, bbox_inches="tight", pad_inches=0.03)

    plt.close()

def create_combined_district_table(collisions_joined, casualties_joined,
                                   vehicles_joined, output_dir, year):
    """
    Create one district summary table with collision, casualty and vehicle counts,
    plus a TOTAL row, and save it as a CSV file.

    Parameters:
    - collisions_joined: GeoDataFrame of collisions joined to districts
    - casualties_joined: GeoDataFrame of casualties joined to districts
    - vehicles_joined: GeoDataFrame of vehicles joined to districts
    - output_dir: folder where the CSV file will be saved
    - year: selected year for analysis

    Returns:
    - combined_table: DataFrame containing district totals and overall total row
    """

    collisions_count = (collisions_joined.groupby("LGDNAME")
                        .size()
                        .rename("collision_count")
                        )

    casualties_count = (casualties_joined.groupby("LGDNAME")
                        .size()
                        .rename("casualties_count")
                        )

    vehicles_count = (
        vehicles_joined.groupby("LGDNAME")
        .size()
        .rename("vehicles_count")
    )

    combined_table = pd.concat(
        [collisions_count, casualties_count, vehicles_count],
        axis=1
    ).fillna(0)

    combined_table = combined_table.astype(int)

    combined_table = combined_table.sort_values(
        "collision_count",
        ascending=False
    )

    total_row = pd.DataFrame({
        "collision_count": [combined_table["collision_count"].sum()],
        "casualties_count": [combined_table["casualties_count"].sum()],
        "vehicles_count": [combined_table["vehicles_count"].sum()]
    }, index=["TOTAL"])

    combined_table = pd.concat([combined_table, total_row])

    combined_table.to_csv(
        output_dir / f"{year}_TABLE_collisions_casualties_vehicles_by_district.csv"
    )

    print(
        f"{year} TABLE collisions_casualties_vehicles_by_district.csv created"
    )

    return combined_table

# Create function for bar charts
def create_bar_chart(series, output_dir, year,
                     title, xlabel, ylabel,
                     output_filename, color=None):
    """
    Create and save a horizontal bar chart from a pandas Series.

    Parameters:
    - series: pandas Series with district names as index and values as counts
    - output_dir: folder where the image will be saved
    - year: selected year for analysis
    - title: chart title
    - xlabel: x-axis label
    - ylabel: y-axis label
    - output_filename: output PNG filename
    - color: optional bar colour

    Returns:
    - saves a PNG chart in the outputs folder
    """

    plt.figure(figsize=(10, 6))

    series.sort_values().plot(
        kind="barh",
        color=color
    )

    plt.title(f"{title} ({year})")
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(axis="x", linestyle="--", alpha=0.7)
    plt.tight_layout()

    plt.savefig(output_dir / output_filename, dpi=300)
    plt.close()

    print(f"{year} GRAPH {title} created")

def create_driver_agegroup_hotspot(joined_vehicles, districts, outline, output_dir, year,
                                   agegroup_code, agegroup_label, output_name):
    """
    Create a hotspot-style map for collisions involving a selected driver age group.

    Parameters:
    - joined_vehicles: vehicle points joined to district boundaries
    - districts: GeoDataFrame of district boundaries
    - outline: GeoDataFrame of Northern Ireland outline
    - output_dir: folder where the map will be saved
    - year: selected year for analysis
    - agegroup_code: driver age group code
    - agegroup_label: label used in the map title
    - output_name: name used for the output file

    Returns:
    - saves a PNG hotspot map in the outputs folder
    """

    driver_group = joined_vehicles[
        joined_vehicles["v_agegroup"] == agegroup_code
    ]

    fig, ax = plt.subplots(figsize=(9, 6.5))

    districts.plot(ax=ax, facecolor="#e6e6e6", edgecolor="grey", linewidth=0.4)
    outline.boundary.plot(ax=ax, color="black", linewidth=1)

    # Adding boundary legend
    add_boundary_legend(ax)

    if not driver_group.empty:
        x = driver_group.geometry.x
        y = driver_group.geometry.y

        hb = ax.hexbin(
            x,
            y,
            gridsize=45,
            cmap="YlOrRd",
            mincnt=1
        )

        plt.colorbar(hb, ax=ax, label="Collision density")

    ax.set_title(f"{agegroup_label} Driver Collision Hotspot ({year})")
    ax.tick_params(axis="both", labelsize=8)

    plt.grid(axis="both", linestyle="--", alpha=0.4)

    add_map_elements(ax)

    plt.tight_layout()
    plt.savefig(
        output_dir / f"{year}_MAP_{output_name}.png",
        dpi=300,
        bbox_inches="tight"
    )
    plt.close()

    print(f"{year} MAP {output_name} created")

# Load shapefiles - NI outline, NI districts
outline = gpd.read_file(DATA_DIR/"ni_outline.shp")
districts = gpd.read_file(DATA_DIR/"ni_districts.shp")

# Loading collision data from CSV into a pandas DataFrame
collisions = pd.read_csv(COLLISION_CSV)

print(f"{YEAR} DATA Collision loaded")

# Creating collision point locations using Easting (a_gd1) and Northing a_gd2)
# CRS: TM65 Irish Grid (EPSG = 29901)
collisions_gdf = gpd.GeoDataFrame(
    collisions,
    geometry=gpd.points_from_xy(collisions["a_gd1"], collisions["a_gd2"]),
    crs="EPSG:29901"
)

# Match crs to collision data
outline = outline.to_crs(epsg=29901)
districts = districts.to_crs(epsg=29901)

# Plot NI outline and districts boundaries
fig, ax = plt.subplots(figsize=(9, 6.5))
districts.plot(ax=ax, facecolor="#e6e6e6", edgecolor="grey", linewidth=0.4)
outline.plot(ax=ax, facecolor="none", edgecolor="black", linewidth=1)


# Plot collision points by severity
fatal_points = collisions_gdf[collisions_gdf["a_type"] == 1]
serious_points = collisions_gdf[collisions_gdf["a_type"] == 2]
slight_points = collisions_gdf[collisions_gdf["a_type"] == 3]

# Plot slight collision first so serious and fatal points appear on top
slight_points.plot(ax=ax, color="yellowgreen", markersize=1)
serious_points.plot(ax=ax, color="orange", markersize=2)
fatal_points.plot(ax=ax, color="maroon", markersize=3)

# Boundaries legend
outline_patch = mpatches.Patch(edgecolor="black", facecolor="none", label="NI Outline")
district_patch = mpatches.Patch(edgecolor="grey", facecolor="none", label="Districts")

# Collisions legend
fatal_patch = mpatches.Patch(color="maroon", label="Fatal")
serious_patch = mpatches.Patch(color="orange", label="Serious")
slight_patch = mpatches.Patch(color="yellowgreen", label="Slight")

ax.legend(handles=[outline_patch, district_patch, fatal_patch, serious_patch, slight_patch],
          loc="upper left",
          bbox_to_anchor=(0.01, 0.99)
)
# Make coordinate numbers smaller
ax.tick_params(axis="both", labelsize=8)

# Adding north arrow, scale and source
add_map_elements(ax)

plt.title(f"Total road traffic collisions in Northern Ireland ({YEAR})")

# Save collision severity point map
plt.savefig(OUTPUT_DIR / f"{YEAR}_MAP_collisions.png", dpi=300, bbox_inches="tight", pad_inches=0.05)

# Remove the # from plt.show() if you want to see the map and add # to the next line
# plt.show()
plt.close()

print(f"{YEAR} MAP total collisions in NI created")

# Creating spatial join - connect collisions to districts
joined = gpd.sjoin(collisions_gdf, districts, how="inner", predicate="within")

# Create grouped series for collision graph
by_district = joined.groupby("LGDNAME").size().sort_values(ascending=False)

# Create graph for collisions by district
create_bar_chart(
    by_district,
    OUTPUT_DIR,
    YEAR,
    "Number of Collisions by District",
    "Collision Count",
    "District",
    f"{YEAR}_GRAPH_collisions_by_district.png"
)

# Load casualty data for the selected year
casualties = pd.read_csv(CASUALTY_CSV)

print(f"{YEAR} DATA Casualties loaded")

# Casualties will be joined with collisions data
collision_casualty = collisions.merge(casualties, on="a_ref", how="inner")

# Dataset is converted into a GeoDataFrame using Easting and Northing from collision
casualties_gdf = gpd.GeoDataFrame(
    collision_casualty,
    geometry=gpd.points_from_xy(collision_casualty["a_gd1"], collision_casualty["a_gd2"]),
    crs="EPSG:29901"
)

# Use spatial join to districts boundaries
joined_casualties = gpd.sjoin(casualties_gdf, districts, how="inner", predicate="within")

# Create grouped series for casualties graph
casualties_by_district = joined_casualties.groupby("LGDNAME").size().sort_values(ascending=False)

# Creating casualties graph
create_bar_chart(
    casualties_by_district,
    OUTPUT_DIR,
    YEAR,
    "Casualties by District",
    "Number of casualties",
    "District",
    f"{YEAR}_GRAPH_casualties_by_district.png",
    color="green"
)

# Load vehicle data for the selected year
vehicles = pd.read_csv(VEHICLE_CSV)

print(f"{YEAR} DATA Vehicles loaded")

# Joining vehicles dataset with collisions data
collision_vehicle = collisions.merge(vehicles, on="a_ref", how="inner")

# Using GeoPandas to convert vehicle data into spatial points using Easting and Northing from collision dataset
vehicles_gdf = gpd.GeoDataFrame(
    collision_vehicle,
    geometry=gpd.points_from_xy(collision_vehicle["a_gd1"], collision_vehicle["a_gd2"]),
    crs="EPSG:29901"
)

# Spatially join vehicle points to district boundaries
joined_vehicles = gpd.sjoin(vehicles_gdf, districts, how="inner", predicate="within")

# Create hotspot map for young drivers (17-24)
create_driver_agegroup_hotspot(
    joined_vehicles,
    districts,
    outline,
    OUTPUT_DIR,
    YEAR,
    agegroup_code=3,
    agegroup_label="Young 17-24",
    output_name="young_driver_17_24_hotspot"
)

# Create hotspot map for older drivers (65+)
create_driver_agegroup_hotspot(
    joined_vehicles,
    districts,
    outline,
    OUTPUT_DIR,
    YEAR,
    agegroup_code=8,
    agegroup_label="Older 65+",
    output_name="older_driver_65_plus_hotspot"
)

# Create grouped series for vehicle graph
vehicles_by_district = joined_vehicles.groupby("LGDNAME").size().sort_values(ascending=False)

# Create one combined table for collisions, casualties and vehicles
combined_table = create_combined_district_table(
    joined,
    joined_casualties,
    joined_vehicles,
    OUTPUT_DIR,
    YEAR
)

# Create graph for vehicle by district
create_bar_chart(
    vehicles_by_district,
    OUTPUT_DIR,
    YEAR,
    "Vehicles by District",
    "Number of vehicles",
    "District",
    f"{YEAR}_GRAPH_vehicles_by_district.png",
    color="orange"
)

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

# Calculate percentages
severity_table["fatal_percentage"] = (severity_table["fatal"] / severity_table["total"] * 100).round(2)
severity_table["serious_percentage"] = (severity_table["serious"] / severity_table["total"] * 100).round(2)
severity_table["slight_percentage"] = (severity_table["slight"] / severity_table["total"] * 100).round(2)

# Calculate ratio (avoid division by zero)
severity_table["serious_to_slight_ratio"] = (severity_table["serious"] / severity_table["slight"].replace(0, pd.NA)
                                             ).round(3)

# Save severity summary table to csv
severity_table.to_csv(OUTPUT_DIR / f"{YEAR}_TABLE_severity_by_district.csv")
print(f"{YEAR} TABLE Severity_by_district.csv created")

# Create bar chart - Collision Severity by District
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
    "Fatal ÷ Total collisions x 100",
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
    "Serious ÷ Total collisions x 100",
    f"{YEAR}_MAP_serious_percentage_choropleth.png",
    "Wistia"
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
    "Slight ÷ Total collisions x 100",
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
    "Serious collisions ÷ Slight collisions",
    f"{YEAR}_MAP_serious_to_slight_ratio_choropleth.png",
    "Purples"
)
print(f"{YEAR} MAP serious_to_slight_ratio_choropleth created")

# End of script