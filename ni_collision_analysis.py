import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

# Load collision data
collisions = pd.read_csv("data/collisions_2024.csv")

# Load NI outline
outline = gpd.read_file("data/NI_outline.shp")

print("Data loaded")

outline.plot()
plt.title("Northern Ireland Outline")
plt.show()