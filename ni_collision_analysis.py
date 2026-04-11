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

plt.title("Northern Ireland Outline")
plt.show()
