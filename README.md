# Northern Ireland Road Traffic Collision Analysis


## Overview
This project analyses police-recorded injury road traffic collisions in Northern Ireland.

The script:
- loads collision, casualty and vehicle CSV files
- create spatial points data from collision coordinates
- loads Northern Ireland outline and district shapefiles
- joins data to district boundaries
- creates maps, graphs and summary tables
- saves outputs as CSV and PNG files

The script can be used for any available year from **2013** to **2025**.


## Data Download

Go to the Open Data NI website:

https://admin.opendatani.gov.uk/dataset/police-recorded-injury-road-traffic-collision-statistics-northern-ireland-2025

Download these three CSV files:

- collision2025.csv
- casualty2025.csv
- vehicle2025.csv

Save all downloaded CSV files inside the project **data** folder.

To use another year, change the year at the end of the website address.


## Boundary Files

Go to the Open Data NI website and download these shapefiles:

https://admin.opendatani.gov.uk/dataset/osni-open-data-largescale-boundaries-local-government-districts-2012

https://admin.opendatani.gov.uk/dataset/osni-open-data-50k-boundaries-ni-outline

Place them in the **data** folder:

- ni_outline.shp
- ni_districts.shp

## Installation

By clicking the green **Code** button on the top of this page, three options are available:

1. Select **Download ZIP** to save the files to your computer and run it in an IDE, such as **PyCharm**
2. Select **Open with GitHub Desktop** - choose the local folder where the repository will be saved, and the project will be cloned automatically. 
3. Select **Copy URL** to use the repository address with GitHub Desktop or the Git command line: https://github.com/MartinCervenka00/ni-traffic-collision-analysis.git 

   The repository may also be cloned using:

```python
git clone http://github.com/MartinCervenka00/ni-traffic-collision-analysis.git
cd ni-traffic-collision-analysis 
```
## Environment
A conda environment is used to guarantee that all required dependencies are installed and that the code can be reproduced. The environment can be created using the provided environment.yml file:

```python
conda env create -f environment.yml
conda activate ni-collisions
```
## Run the Script in PyCharm
1. Open PyCharm
2. Select **Open Project** and choose the project folder:
    - `ni-traffic-collision-analysis`
3. Make sure the correct interpreter is selected:
   - `File > Settings > Python Interpreter`

4. Choose the conda environment:
   - `ni-collisions`

5. In the Project panel, open:
   - `ni_collision_analysis.py`
   
6. Change the year in the script if required:

```python
YEAR = 2025
```
The script will automatically load:
- collision2025.csv
- casualty2025.csv
- vehicle2025.csv

7. Click the green **Run** button in the top-right corner of PyCharm.


8. If successful, the terminal should show:


```text
Process finished with exit code 0
```

## Outputs

Results are saved in the **output** folder as PNG charts/maps and CSV summary tables.


## Maps

### Collision Locations
![Collision Locations](output/2025_MAP_collisions.png)

### Fatal Percentage by District
![Fatal Percentage by District](output/2025_MAP_fatal_percentage_choropleth.png)

### Serious Percentage by District
![Serious Percentage by District](output/2025_MAP_serious_percentage_choropleth.png)

### Slight Percentage by District
![Slight Percentage by District](output/2025_MAP_slight_percentage_choropleth.png)

### Serious to Slight Ratio by District
![Serious to Slight Ratio by District](output/2025_MAP_serious_to_slight_ratio_choropleth.png)


## Graphs

### Casualties by District
![Casualties by District](output/2025_GRAPH_casualties_by_district.png)

### Collisions by District
![Collisions by District](output/2025_GRAPH_collisions_by_district.png)

### Vehicles by District
![Vehicles by District](output/2025_GRAPH_vehicles_by_district.png)

### Collision Severity by District
![Collision Severity by District](output/2025_GRAPH_severity_by_district.png)


## CSV Tables

### District Summary Tables

table will be added after joining them together

## Collision Severity by District (2025)

| District | Fatal | Serious | Slight | Total | Fatal % | Serious % | Slight % | Serious/Slight Ratio |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Antrim and Newtownabbey | 6 | 52 | 359 | 417 | 1.44 | 12.47 | 86.09 | 0.145 |
| Ards and North Down | 7 | 56 | 290 | 353 | 1.98 | 15.86 | 82.15 | 0.193 |
| Armagh City, Banbridge and Craigavon | 5 | 108 | 441 | 554 | 0.90 | 19.49 | 79.60 | 0.245 |
| Belfast | 5 | 161 | 966 | 1132 | 0.44 | 14.22 | 85.34 | 0.167 |
| Causeway Coast and Glens | 7 | 74 | 265 | 346 | 2.02 | 21.39 | 76.59 | 0.279 |
| Derry City and Strabane | 0 | 54 | 303 | 357 | 0.00 | 15.13 | 84.87 | 0.178 |
| Fermanagh and Omagh | 4 | 58 | 221 | 283 | 1.41 | 20.49 | 78.09 | 0.262 |
| Lisburn and Castlereagh | 2 | 87 | 337 | 426 | 0.47 | 20.42 | 79.11 | 0.258 |
| Mid Ulster | 9 | 70 | 287 | 366 | 2.46 | 19.13 | 78.42 | 0.244 |
| Mid and East Antrim | 2 | 60 | 228 | 290 | 0.69 | 20.69 | 78.62 | 0.263 |
| Newry, Mourne and Down | 6 | 114 | 371 | 491 | 1.22 | 23.22 | 75.56 | 0.307 |

## Notes

- Coordinate system used: **TM65 / Irish Grid (EPSG:29901)**
- Collision points are created from:
  - `a_gd1` = Easting
  - `a_gd2` = Northing


## Author

Martin Cervenka