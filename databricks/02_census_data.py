# Databricks notebook source
# MAGIC %run /Users/linh.nguyennnn@outlook.com/00_setup

# COMMAND ----------

import requests
import pandas as pd

# Census API Key - Get yours free at: https://api.census.gov/data/key_signup.html
CENSUS_API_KEY = "YOUR_CENSUS_API_KEY_HERE"

print("Census API Ready!")

# COMMAND ----------

# Census variables:
# B19013_001E = Median Household Income
# B25077_001E = Median Home Value
# B01003_001E = Total Population
# B15003_022E = Bachelor's Degree holders
# B15003_001E = Total Population 25+ (for education %)
# B03002_001E = Total Population (for diversity)
# B03002_003E = White alone non-Hispanic (for diversity calc)

variables = "NAME,B19013_001E,B25077_001E,B01003_001E,B15003_022E,B15003_001E,B03002_001E,B03002_003E"

# Fetch all places in Texas (state code 48)
url = f"https://api.census.gov/data/2022/acs/acs5?get={variables}&for=place:*&in=state:48&key={CENSUS_API_KEY}"

response = requests.get(url)
data = response.json()

# Convert to DataFrame
columns = data[0]
rows = data[1:]
census_df = pd.DataFrame(rows, columns=columns)

print(f"Fetched {len(census_df)} Texas cities!")
census_df.head(10)

# COMMAND ----------

census_df = census_df.rename(columns ={
    'NAME': 'CITY_NAME',
    'B19013_001E': 'MEDIAN_INCOME',
    'B25077_001E': 'MEDIAN_HOME_VALUE',
    'B01003_001E': 'POPULATION',
    'B15003_022E': 'BACHELORS_DEGREE',
    'B15003_001E': 'POPULATION_25PLUS',
    'B03002_001E': 'TOTAL_POP_RACE',
    'B03002_003E': 'WHITE_NON_HISPANIC',
    'state': 'STATE_CODE',
    'place': 'PLACE_CODE'
})

# Convert to numeric
numeric_cols = ['MEDIAN_INCOME', 'MEDIAN_HOME_VALUE', 'POPULATION', 
                'BACHELORS_DEGREE', 'POPULATION_25PLUS', 'TOTAL_POP_RACE', 'WHITE_NON_HISPANIC']
for col in numeric_cols:
  census_df[col] = pd.to_numeric(census_df[col], errors='coerce')

# Clean city names (remove ", Texas" suffix)
census_df['CITY'] = census_df['CITY_NAME'].str.replace(' city, Texas', '').str.replace(' town, Texas', '').str.replace(' CDP, Texas', '')

print("Columns renamed!")
census_df.head(10)

# COMMAND ----------

# Get DFW cities from your Redfin SILVER data (has PARENT_METRO_REGION)
silver_df = spark.read.format("delta").load(silver_path)

# Filter to Dallas metro area only
dfw_redfin = silver_df.filter(
    silver_df.PARENT_METRO_REGION.contains("Dallas")
).select("CITY").distinct().toPandas()

dfw_cities_list = dfw_redfin['CITY'].tolist()

print(f"Found {len(dfw_cities_list)} cities in DFW metro from Redfin!")

# Calculate diversity index (% non-white)
census_df['DIVERSITY_PCT'] = round((1 - (census_df['WHITE_NON_HISPANIC'] / census_df['TOTAL_POP_RACE'])) * 100, 1)

# Calculate education rate (% with bachelor's degree)
census_df['BACHELORS_PCT'] = round((census_df['BACHELORS_DEGREE'] / census_df['POPULATION_25PLUS']) * 100, 1)

# Filter Census to DFW cities
dfw_census = census_df[census_df['CITY'].isin(dfw_cities_list)]

print(f"Matched {len(dfw_census)} cities with Census data!")
dfw_census[['CITY', 'POPULATION', 'MEDIAN_INCOME', 'MEDIAN_HOME_VALUE', 'DIVERSITY_PCT', 'BACHELORS_PCT']].sort_values('POPULATION', ascending=False).head(20)

# COMMAND ----------

# Convert to Spark DataFrame and save
census_spark_df = spark.createDataFrame(dfw_census)

# Save to Azure Storage
census_path = f"{path}census/dfw_census_data"
census_spark_df.write.format("delta").mode("overwrite").save(census_path)

print("Census data saved to Azure Storage")

# COMMAND ----------

# Verify it saved
spark.read.format("delta").load(census_path).show(10)
