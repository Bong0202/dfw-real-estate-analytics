# Databricks notebook source
# MAGIC %run /Users/linh.nguyennnn@outlook.com/00_setup

# COMMAND ----------

#Load all 7 Redfin files
national_df = spark.read.option("header", "true").option("delimiter", "\t").csv(f"{path}us_national_market_tracker.tsv000")
state_df = spark.read.option("header", "true").option("delimiter", "\t").csv(f"{path}state_market_tracker.tsv000.gz")
metro_df = spark.read.option("header", "true").option("delimiter", "\t").csv(f"{path}redfin_metro_market_tracker.tsv000.gz")
county_df = spark.read.option("header", "true").option("delimiter", "\t").csv(f"{path}county_market_tracker.tsv000.gz")
city_df = spark.read.option("header", "true").option("delimiter", "\t").csv(f"{path}city_market_tracker.tsv000.gz")
zip_df = spark.read.option("header", "true").option("delimiter", "\t").csv(f"{path}zip_code_market_tracker.tsv000.gz")
neighborhood_df = spark.read.option("header", "true").option("delimiter", "\t").csv(f"{path}neighborhood_market_tracker.tsv000.gz")

#Check row count
print(f"National: {national_df.count():,} rows")
print(f"State: {state_df.count():,} rows")
print(f"Metro: {metro_df.count():,} rows")
print(f"County: {county_df.count():,} rows")
print(f"City: {city_df.count():,} rows")
print(f"Zip Code: {zip_df.count():,} rows")
print(f"Neighborhood: {neighborhood_df.count():,} rows")

# COMMAND ----------

# See all columns in the city data
city_df.printSchema()

# COMMAND ----------

#Filter city data to Texas only
texas_cities_df = city_df.filter(city_df.STATE_CODE == "TX")

# Show Dallas-Fort Worth area cities
texas_cities_df.filter(
    texas_cities_df.PARENT_METRO_REGION.contains("Dallas")
).select("CITY", "STATE", "PARENT_METRO_REGION", "MEDIAN_SALE_PRICE", "PERIOD_END").show(20)

# COMMAND ----------

# BRONZE LAYER: Save to Azure storage
bronze_path = f"{path}bronze/texas_cities/"
texas_cities_df.write.format("delta").mode("overwrite").save(bronze_path)

print("Bronze layer saved!")

# COMMAND ----------

from pyspark.sql.functions import col, to_date, when
from pyspark.sql.types import DoubleType, IntegerType

# SILVER LAYER: Clean and transform data
# Replace 'NA' with null first, then cast
silver_df = spark.read.format("delta").load(bronze_path) \
    .withColumn("PERIOD_END_DATE", to_date(col("PERIOD_END"))) \
    .withColumn("MEDIAN_SALE_PRICE", when(col("MEDIAN_SALE_PRICE") == "NA", None).otherwise(col("MEDIAN_SALE_PRICE")).cast(DoubleType())) \
    .withColumn("MEDIAN_LIST_PRICE", when(col("MEDIAN_LIST_PRICE") == "NA", None).otherwise(col("MEDIAN_LIST_PRICE")).cast(DoubleType())) \
    .withColumn("MEDIAN_PPSF", when(col("MEDIAN_PPSF") == "NA", None).otherwise(col("MEDIAN_PPSF")).cast(DoubleType())) \
    .withColumn("HOMES_SOLD", when(col("HOMES_SOLD") == "NA", None).otherwise(col("HOMES_SOLD")).cast(IntegerType())) \
    .withColumn("INVENTORY", when(col("INVENTORY") == "NA", None).otherwise(col("INVENTORY")).cast(IntegerType())) \
    .withColumn("MEDIAN_DOM", when(col("MEDIAN_DOM") == "NA", None).otherwise(col("MEDIAN_DOM")).cast(IntegerType())) \
    .filter(col("MEDIAN_SALE_PRICE").isNotNull())

# Save Silver layer
silver_path = f"{path}silver/texas_cities_cleaned"
silver_df.write.format("delta").mode("overwrite").save(silver_path)

print(f"Silver layer saved!")

# COMMAND ----------

from pyspark.sql.functions import avg, sum, count, year, month

# GOLD LAYER: Aggregated analytics
gold_df = spark.read.format("delta").load(silver_path) \
    .withColumn("YEAR", year(col("PERIOD_END_DATE"))) \
    .withColumn("MONTH", month(col("PERIOD_END_DATE"))) \
    .groupBy("CITY", "YEAR", "PROPERTY_TYPE") \
    .agg(
        avg("MEDIAN_SALE_PRICE").alias("AVG_SALE_PRICE"),
        avg("MEDIAN_PPSF").alias("AVG_PRICE_PER_SQFT"),
        sum("HOMES_SOLD").alias("TOTAL_HOMES_SOLD"),
        avg("MEDIAN_DOM").alias("AVG_DAYS_ON_MARKET"),
        avg("INVENTORY").alias("AVG_INVENTORY")
    ) \
    .orderBy("CITY", "YEAR")

# Save Gold Layer
gold_path = f"{path}gold/texas_market_summary"
gold_df.write.format("delta").mode("overwrite").save(gold_path)

print("Gold layer saved!")

# COMMAND ----------

# View the Gold layer results
gold_df.show(20)

# COMMAND ----------

gold_df = spark.read.format("delta").load(gold_path)
gold_df.show(10)

# COMMAND ----------

gold_df.createOrReplaceTempView("texas_market")
print("SQL table 'texas_market' created!")

# COMMAND ----------

# SQL Query: Top 10 most expensive Dallas-area city in 2024
spark.sql("""
    SELECT
        CITY,
        ROUND(AVG(AVG_SALE_PRICE), 0) as AVG_PRICE,
        ROUND(AVG(AVG_DAYS_ON_MARKET), 0) as AVG_DOM,
        SUM(TOTAL_HOMES_SOLD) as TOTAL_SOLD
    FROM texas_market
    WHERE YEAR = 2024
        AND PROPERTY_TYPE = 'All Residential'
    GROUP BY CITY
    ORDER BY AVG_PRICE DESC
    LIMIT 10
""").show()

# COMMAND ----------

# Year over year comparison for Dallas
spark.sql("""
    SELECT
        YEAR,
        ROUND(AVG(AVG_SALE_PRICE), 0) as AVG_PRICE,
        ROUND(SUM(TOTAL_HOMES_SOLD), 0) as TOTAL_SOLD
    FROM texas_market
    WHERE CITY = 'Dallas'
        AND PROPERTY_TYPE = 'All Residential'
        AND YEAR >= 2018
    GROUP BY YEAR
    ORDER BY YEAR
""").show()

# COMMAND ----------

spark.sql("""
    SELECT
        CITY,
        YEAR,
        ROUND(AVG_SALE_PRICE, 0) as AVG_PRICE,
        ROUND(AVG_DAYS_ON_MARKET, 0) as DAYS_ON_MARKET
    FROM texas_market
    WHERE CITY IN ('Coppell', 'Grapevine', 'Plano', 'Euless', 'Irving')
        AND PROPERTY_TYPE = 'All Residential'
        AND YEAR >= 2022
    ORDER BY CITY, YEAR          
""").show(50)

# COMMAND ----------

# Window Function: Year over year price change
spark.sql("""
    SELECT
        CITY,
        YEAR,
        ROUND(AVG_SALE_PRICE, 0) as AVG_PRICE,
        ROUND(AVG_SALE_PRICE - LAG(AVG_SALE_PRICE) OVER (PARTITION BY CITY ORDER BY YEAR), 0) as PRICE_CHANGE,
        ROUND(((AVG_SALE_PRICE - LAG(AVG_SALE_PRICE) OVER (PARTITION BY CITY ORDER BY YEAR)) / LAG(AVG_SALE_PRICE) OVER (PARTITION BY CITY ORDER BY YEAR)) * 100, 1) as PCT_CHANGE
    FROM texas_market
    WHERE CITY IN ('Coppell', 'Grapevine', 'Plano', 'Euless', 'Irving')
        AND PROPERTY_TYPE = 'All Residential'
        AND YEAR >= 2020
    ORDER BY CITY, YEAR          
""").show(50)

# COMMAND ----------

