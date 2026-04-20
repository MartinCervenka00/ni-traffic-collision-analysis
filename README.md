# Northern Ireland Traffic Collision Analysis


## Overview
This project analyses police-recorded injury road traffic collisions in Northern Ireland.

The script:
- loads collision, casualty and vehicle CSV files
- create spatial points data from collision coordinates
- loads Northern Ireland outline and district shapefiles
- joins data to district boundaries
- creates maps, graphs and summary tables
- saves outputs as CSV and PNG files

The script can be used for any available year from **2013** to **2024**.


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

Create an environment:
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
YEAR = 2024
```
The script will automatically load:
- collision2025.csv
- casualty2025.csv
- vehicle2025.csv

7. Click the green Run button in the top-right corner of PyCharm.


8. If successful, the terminal should show:


```text
Process finished with exit code 0
```


## Outputs
Results are saved in the **Outputs** folder.

These include:

- collision map
- collisions by district CSV
- collisions by district graph
- casualties by district CSV
- casualties by district graph
- vehicles by district CSV
- vehicles by district graph
- fatal collisions by district choropleth map
- collision severity by district CSV
- collision severity by district graph

Each CSV file includes a final TOTAL row.


## Notes

- Coordinate system used: **TM65 / Irish Grid (EPSG:29901)**
- Collision points are created from:
  - `a_gd1` = Easting
  - `a_gd2` = Northing


## Author

Martin Cervenka