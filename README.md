# Police Recorded Injury Road Traffic Collision Statistics Northern Ireland 2024 

## Overview
This project analyses the spatial distribution of police-recorded injury road traffic collisions in Northern Ireland using Python and GeoPandas.

#The script:
- loads collision CSV data
- creates spatial points using Easting/Northing (EPSG:29901)
- loads NI outline and district shapefiles
- plots collisions on a map
- performs spatial join with districts
- counts collisions by district
- saves results as CSV and PNG
