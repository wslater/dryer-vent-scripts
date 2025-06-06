# Dryer Vent Opportunity Analysis Tool

This script generates a list of ZIP codes within a 30-minute driving area from Morrisville, NC, and ranks them based on an "Adjusted Opportunity Score" — calculated as:

```
Adjusted Opportunity Score = Total_Single_Family_Homes × Median_Household_Income
```

It combines shapefile data, housing data from the U.S. Census, and real-time API access to income estimates by ZIP code.

---

## 🔧 Setup Instructions

### 1. Install Python 3 (if not already installed)
On macOS, we recommend using [Homebrew](https://brew.sh/):

```bash
brew install python
```

Verify installation:

```bash
python3 --version
```

---

### 2. Clone the Project and Create a Virtual Environment

```bash
mkdir dryer-vent-analysis
cd dryer-vent-analysis
python3 -m venv venv
source venv/bin/activate
```

---

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install pandas geopandas shapely requests
```

> Note: If you get errors installing `geopandas`, you may need to run `brew install gdal` first, or install via conda.

---

### 4. Download Required Files

Place the following files in your project directory:

- `isochrone_zip_by_income.py` – the main script
- `ACSDT5Y2023.B25024-Data.csv` – housing unit data by ZIP
- Shapefile components for U.S. ZIP Code Tabulation Areas:
  - `cb_2023_us_zcta520_500k.shp`
  - `cb_2023_us_zcta520_500k.shx`
  - `cb_2023_us_zcta520_500k.dbf`
  - `cb_2023_us_zcta520_500k.prj`
  - (and any others from the ZIP)

These files can be downloaded from the [U.S. Census TIGER/Line Shapefiles](https://www.census.gov/cgi-bin/geo/shapefiles/index.php?year=2023&layergroup=ZIP+Code+Tabulation+Areas).

---

### 5. Run the Script

```bash
python isochrone_zip_by_income.py
```

The script will:
- Simulate a 30-minute isochrone around Morrisville, NC
- Filter ZIP codes within the area
- Pull income data from the Census API
- Calculate opportunity scores
- Save the results to:

```
zips_with_income_score.csv
```

---

## 🗺️ Output Example

| ZIP Code | Total_Single_Family_Homes | Median_Household_Income | Adjusted_Opportunity_Score |
|----------|----------------------------|--------------------------|-----------------------------|
| 27519    | 7000                       | 130000                   | 910,000,000                 |
| 27560    | 5000                       | 115000                   | 575,000,000                 |


