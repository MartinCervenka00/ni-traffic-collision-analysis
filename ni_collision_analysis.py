import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

# Load collision data
collisions = pd.read_csv("data/collisions_2024.csv")

# Load NI outline
outline = gpd.read_file("data/NI_outline.shp")

print("Data loaded")

# Changing map to black line with width 1 with no face colour
fig, ax = plt.subplots()
outline.plot(ax=ax, facecolor="none", edgecolor="black", linewidth=1)


# Creating collision points (TM65 Irish Grid - EPSG = 29901, where a_gd1 = Easting and a_gd2 = Northing)
collisions_gdf = gpd.GeoDataFrame(
    collisions,
    geometry=gpd.points_from_xy(collisions["a_gd1"], collisions["a_gd2"]),
    crs="EPSG:29901"
)

# Match crs to collision data
outline = outline.to_crs(epsg=29901)

# Area is being plotted for both ni outline and collision
fig, ax = plt.subplots()
outline.plot(ax=ax, color="white", edgecolor="black")
collisions_gdf.plot(ax=ax, color="red", markersize=1)


plt.title("Road traffic collisions in Northern Ireland (2024)")
plt.show()