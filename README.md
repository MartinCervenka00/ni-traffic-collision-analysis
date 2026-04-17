# Northern Ireland Traffic Collision Analysis


## Overview
This project analyses police-recorded injury road traffic collisions in Northern Ireland.

The script:
- loads collision, casualty and vehicle CSV files
- creates spatial points from collision coordinates
- loads Northern Ireland outline and district shapefiles
- joins data to district boundaries
- creates maps, graphs and summary tables
- saves outputs as CSV and PNG files

The script can be used for any available year from **2013** to **2024**.


## Data Download

Go to the Open Data NI website:

https://admin.opendatani.gov.uk/dataset/police-recorded-injury-road-traffic-collision-statistics-northern-ireland-2024

To use another year, change the year at the end of the website address:

Examples:

- 2023  
https://admin.opendatani.gov.uk/dataset/police-recorded-injury-road-traffic-collision-statistics-northern-ireland-2023

- 2022  
https://admin.opendatani.gov.uk/dataset/police-recorded-injury-road-traffic-collision-statistics-northern-ireland-2022

Download these three CSV files:

- collisionYYYY.csv
- casualtyYYYY.csv
- vehicleYYYY.csv

Example for 2024:

- collision2024.csv
- casualty2024.csv
- vehicle2024.csv

Save all downloaded CSV files inside the project **data** folder.


## Boundary Files Needed

Go to the Open Data NI website and download these shapefiles:

https://admin.opendatani.gov.uk/dataset/osni-open-data-largescale-boundaries-local-government-districts-2012

https://admin.opendatani.gov.uk/dataset/osni-open-data-50k-boundaries-ni-outline

Place them in the **data** folder:

- ni_outline.shp
- ni_districts.shp

## Instalation


## Select the Year

At the top of the Python script (ni_collision_analysis.py), change:

```python
YEAR = 2024
```

The script will automatically load:

- collision2024.csv
- casualty2024.csv
- vehicle2024.csv

---

## Run the Script

---

## Outputs

---

## Troubleshooting

If successful, the terminal should show:

```text
Process finished with exit code 0
```

---
## Author

Martin Cervenka