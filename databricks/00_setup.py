# Databricks notebook source
#  === MASTER SETUP: Run from other notebooks with %run ./00_setup ===
storage_account_name = "strealestatedatalinh"
container_name = "raw-data"
storage_account_key = "YOUR_STORAGE_ACCOUNT_KEY_HERE"  # Replace with your key

# Use WASB protocol (classic Blob Storage)
spark.conf.set(
    f"fs.azure.account.key.{storage_account_name}.blob.core.windows.net", 
    storage_account_key
)

# Use wasbs:// protocol
path = f"wasbs://{container_name}@{storage_account_name}.blob.core.windows.net/"
bronze_path = f"{path}bronze/texas_cities"
silver_path = f"{path}silver/texas_cities_cleaned"
gold_path = f"{path}gold/texas_market_summary"
print("Connected! Ready to go.")
