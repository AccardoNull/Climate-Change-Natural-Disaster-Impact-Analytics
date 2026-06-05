import pandas as pd

# load raw datasets
disasters = pd.read_excel("data/raw/em_dat.xlsx")
temps = pd.read_excel("data/raw/temperature_anomaly.xlsx")
# Rename the columnn
disasters = disasters.rename(columns={"Start Year": "Year"})
# Keep relevant disaster columns
disasters_clean = disasters[[
    "DisNo.",
    "Country",
    "Year",
    "Disaster Type"
]].copy()
temps_clean = temps[["Country", "Year", "Temp_Anomaly"]].copy()
# Keep only climate-related disaster types
climate_disaster_types = [
    "Flood",
    "Storm",
    "Mass movement (wet)",
    "Glacial lake outburst flood",
    "Wildfire",
    "Drought",
    "Extreme temperature"
]
climate_disasters = disasters_clean[
    disasters_clean["Disaster Type"].isin(climate_disaster_types)
].copy()

# Remove regional data
temps_clean = temps_clean[~temps["Country"].str.contains("NIAID",na=False)]
# Remove data before 2000
temps_clean = temps_clean[temps_clean["Year"] >= 2000]
# Clean text
disasters_clean["Country"] = disasters_clean["Country"].astype(str).str.strip()
temps_clean["Country"] = temps_clean["Country"].astype(str).str.strip()
# Clean numeric fields
disasters_clean["Year"] = pd.to_numeric(disasters_clean["Year"], errors="coerce")
temps_clean["Year"] = pd.to_numeric(temps_clean["Year"], errors="coerce")
temps_clean["Temp_Anomaly"] = pd.to_numeric(
    temps_clean["Temp_Anomaly"],
    errors="coerce"
)
# Drop unusable rows
disasters_clean = disasters_clean.dropna(subset=["Country", "Year"])
temps_clean = temps_clean.dropna(subset=["Country", "Year", "Temp_Anomaly"])
# Convert year
disasters_clean["Year"] = disasters_clean["Year"].astype(int)
temps_clean["Year"] = temps_clean["Year"].astype(int)

# Aggregate climate-related disasters by country-year
disaster_summary = (
    climate_disasters
    .groupby(["Country", "Year"])
    .agg(Climate_Disaster_Count=("DisNo.", "count"))
    .reset_index()
)
# Merge climate + disaster data
goal_dataset = pd.merge(
    temps_clean,
    disaster_summary,
    on=["Country", "Year"],
    how="left"
)
# Countries/years with no disaster record become 0
goal_dataset = pd.merge(
    temps_clean,
    disaster_summary,
    on=["Country", "Year"],
    how="left"
)

goal_dataset["Climate_Disaster_Count"] = (
    goal_dataset["Climate_Disaster_Count"]
    .fillna(0)
    .astype(int)
)

# Save processed dataset
goal_dataset.to_csv(
    "data/processed/country_year_temperature_climate_disasters.csv",
    index=False
)

print(goal_dataset.head())
print(goal_dataset.shape)
print(goal_dataset.isnull().sum())
print(goal_dataset["Climate_Disaster_Count"].describe())
print((goal_dataset["Climate_Disaster_Count"] == 0).sum())
correlation = goal_dataset["Temp_Anomaly"].corr(goal_dataset["Climate_Disaster_Count"])
print("Correlation = ", correlation)
annual = (
    goal_dataset
    .groupby("Year")
    .agg(
        Avg_Temp=("Temp_Anomaly", "mean"),
        Climate_Disasters=("Climate_Disaster_Count", "sum")
    )
    .reset_index()
)
print(annual)