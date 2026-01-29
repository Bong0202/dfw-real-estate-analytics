# Databricks notebook source
# MAGIC %run /Users/linh.nguyennnn@outlook.com/00_setup

# COMMAND ----------

import requests
import pandas as pd

# BLS API (no key required for basic access)
print("✅ BLS API ready!")

# COMMAND ----------

# BLS API - Get DFW Metro Unemployment Rate
# Series ID format for metros: LAUMT48191000000003
# 48 = Texas, 19100 = Dallas-Fort Worth metro

url = "https://api.bls.gov/publicAPI/v2/timeseries/data/"

payload = {
    "seriesid": ["LAUMT481910000000003"],  # DFW unemployment rate
    "startyear": "2022",
    "endyear": "2024"
}

response = requests.post(url, json=payload)

if response.status_code == 200:
    data = response.json()
    
    if data['Results']['series'][0]['data']:
        series_data = data['Results']['series'][0]['data']
        bls_df = pd.DataFrame(series_data)
        print("BLS data fetched!")
        print(bls_df[['year', 'period', 'periodName', 'value']].head(12))
    else:
        print("No data returned. Let's try a different series.")
        print(data)
else:
    print(f"Error: {response.status_code}")
    print(response.text)

# COMMAND ----------

# Add metro area identifier
bls_df['METRO_AREA'] = 'Dallas-Fort Worth'
bls_df['UNEMPLOYMENT_RATE'] = pd.to_numeric(bls_df['value'])

# Keep useful columns
bls_clean = bls_df[['METRO_AREA', 'year', 'periodName', 'UNEMPLOYMENT_RATE']].rename(columns={
    'year': 'YEAR',
    'periodName': 'MONTH'
})

# Convert to Spark DataFrame and save
bls_spark_df = spark.createDataFrame(bls_clean)

bls_path = f"{path}bls/dfw_unemployment"
bls_spark_df.write.format("delta").mode("overwrite").save(bls_path)

print("BLS data saved!")
bls_clean.head(12)

# COMMAND ----------

