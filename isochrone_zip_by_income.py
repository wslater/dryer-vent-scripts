import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
import requests

# --- CONFIGURATION ---
lon, lat = -78.8260, 35.8587
zip_shapefile_path = "tl_2024_us_zcta520.shp"
housing_csv_path = "ACSDT5Y2023.B25024-Data.csv"
output_csv_path = "zips_with_income_score.csv"

# --- STEP 1: Load ZIP Shapefile ---
zip_gdf = gpd.read_file(zip_shapefile_path)
zip_gdf = zip_gdf.to_crs(epsg=3857)

# --- STEP 2: Create 30 km Buffer ---
center = Point(lon, lat)
center_gdf = gpd.GeoDataFrame(geometry=[center], crs="EPSG:4326").to_crs(epsg=3857)
iso_buffer = center_gdf.buffer(30000)
iso_gdf = gpd.GeoDataFrame(geometry=iso_buffer, crs="EPSG:3857")

# --- STEP 3: Spatial Join ---
zip_within_iso = gpd.sjoin(zip_gdf, iso_gdf, predicate='intersects')

# --- STEP 4: Load Housing Data ---
housing_df = pd.read_csv(housing_csv_path, skiprows=1)
housing_df["ZIP Code"] = housing_df["Geography"].str.extract(r'(\d{5})$')

housing_clean = housing_df[[
    "ZIP Code",
    "Estimate!!Total:",
    "Estimate!!Total:!!1, detached",
    "Estimate!!Total:!!1, attached"
]].rename(columns={
    "Estimate!!Total:": "Total_Housing_Units",
    "Estimate!!Total:!!1, detached": "Single_Family_Detached",
    "Estimate!!Total:!!1, attached": "Single_Family_Attached"
})

for col in ["Total_Housing_Units", "Single_Family_Detached", "Single_Family_Attached"]:
    housing_clean[col] = pd.to_numeric(housing_clean[col], errors="coerce")

housing_clean["Total_Single_Family_Homes"] = (
    housing_clean["Single_Family_Detached"] + housing_clean["Single_Family_Attached"]
)

# --- STEP 5: Get Income Data from Census API ---
print("Fetching median household income data from Census...")

try:
    census_url = "https://api.census.gov/data/2022/acs/acs5"
    params = {
        "get": "NAME,B19013_001E",
        "for": "zip code tabulation area:*"
    }
    response = requests.get(census_url, params=params)
    response.raise_for_status()

    data = response.json()
    income_df = pd.DataFrame(data[1:], columns=["Name", "Median_Household_Income", "ZIP Code"])
    income_df["Median_Household_Income"] = pd.to_numeric(income_df["Median_Household_Income"], errors="coerce")

    print(f"✅ Pulled {len(income_df)} ZIPs with income data.")

except Exception as e:
    print("❌ Failed to fetch income data:")
    print(e)
    income_df = pd.DataFrame(columns=["ZIP Code", "Median_Household_Income"])

# --- STEP 6: Merge All Data ---
print("Sample ZIPs from spatial layer:", zip_within_iso["ZCTA5CE20"].head())
print("Sample ZIPs from income data:", income_df["ZIP Code"].head())

zip_within_iso["ZCTA5CE20"] = zip_within_iso["ZCTA5CE20"].astype(str)
merged = (
    zip_within_iso.merge(housing_clean, left_on="ZCTA5CE20", right_on="ZIP Code", how="left")
                  .merge(income_df, on="ZIP Code", how="left")
)

# --- STEP 7: Add Score and Export ---
merged["Adjusted_Opportunity_Score"] = (
    merged["Total_Single_Family_Homes"] * merged["Median_Household_Income"]
)

final = merged[[
    "ZIP Code",
    "Total_Single_Family_Homes",
    "Median_Household_Income",
    "Adjusted_Opportunity_Score"
]].drop_duplicates().sort_values("Adjusted_Opportunity_Score", ascending=False)

final.to_csv(output_csv_path, index=False)
print(f"✅ Output saved to: {output_csv_path}")
