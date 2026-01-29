# Databricks notebook source
# MAGIC %run /Users/linh.nguyennnn@outlook.com/00_setup

# COMMAND ----------

# Load all your data
census_path = f"{path}census/dfw_census_data"
bls_path = f"{path}bls/dfw_unemployment"

# Load Census (city-level)
census_df = spark.read.format("delta").load(census_path).toPandas()

# Load BLS (metro-level)
bls_df = spark.read.format("delta").load(bls_path).toPandas()

# Load Redfin Gold (city-level, latest year)
gold_df = spark.read.format("delta").load(gold_path)
redfin_df = gold_df.filter(
    (gold_df.YEAR == 2024) & 
    (gold_df.PROPERTY_TYPE == "All Residential")
).toPandas()

print(f"Census: {len(census_df)} cities")
print(f"BLS: {len(bls_df)} months of data")
print(f"Redfin: {len(redfin_df)} cities")

# COMMAND ----------

# Check city name samples from both sources
print("Census city names sample:")
print(census_df['CITY'].head(10).tolist())
print("\nRedfin city names sample:")
print(redfin_df['CITY'].head(10).tolist())

# COMMAND ----------

# Merge Census and Redfin on CITY name
combined_df = census_df.merge(
    redfin_df[['CITY', 'AVG_SALE_PRICE', 'AVG_PRICE_PER_SQFT', 'TOTAL_HOMES_SOLD', 'AVG_DAYS_ON_MARKET']],
    on='CITY',
    how='inner'
)

# Add DFW unemployment rate (same for all cities)
latest_unemployment = bls_df[bls_df['YEAR'] == '2024']['UNEMPLOYMENT_RATE'].mean()
combined_df['UNEMPLOYMENT_RATE'] = latest_unemployment

print(f" Combined: {len(combined_df)} DFW cities with all data")
combined_df[['CITY', 'POPULATION', 'MEDIAN_INCOME', 'AVG_SALE_PRICE', 'DIVERSITY_PCT', 'BACHELORS_PCT', 'UNEMPLOYMENT_RATE']].head(15)

# COMMAND ----------

# Create ranking scores (higher = better)
# Normalize each metric to 0-100 scale

from sklearn.preprocessing import MinMaxScaler

# Select metrics for ranking
ranking_df = combined_df.copy()

# For these metrics: HIGHER is BETTER
ranking_df['INCOME_SCORE'] = (ranking_df['MEDIAN_INCOME'] - ranking_df['MEDIAN_INCOME'].min()) / (ranking_df['MEDIAN_INCOME'].max() - ranking_df['MEDIAN_INCOME'].min()) * 100

ranking_df['EDUCATION_SCORE'] = (ranking_df['BACHELORS_PCT'] - ranking_df['BACHELORS_PCT'].min()) / (ranking_df['BACHELORS_PCT'].max() - ranking_df['BACHELORS_PCT'].min()) * 100

ranking_df['DIVERSITY_SCORE'] = (ranking_df['DIVERSITY_PCT'] - ranking_df['DIVERSITY_PCT'].min()) / (ranking_df['DIVERSITY_PCT'].max() - ranking_df['DIVERSITY_PCT'].min()) * 100

# For these metrics: LOWER is BETTER (invert the score)
ranking_df['AFFORDABILITY_SCORE'] = (1 - (ranking_df['AVG_SALE_PRICE'] - ranking_df['AVG_SALE_PRICE'].min()) / (ranking_df['AVG_SALE_PRICE'].max() - ranking_df['AVG_SALE_PRICE'].min())) * 100

ranking_df['MARKET_SPEED_SCORE'] = (1 - (ranking_df['AVG_DAYS_ON_MARKET'] - ranking_df['AVG_DAYS_ON_MARKET'].min()) / (ranking_df['AVG_DAYS_ON_MARKET'].max() - ranking_df['AVG_DAYS_ON_MARKET'].min())) * 100

print("Scores calculated!")
ranking_df[['CITY', 'INCOME_SCORE', 'EDUCATION_SCORE', 'DIVERSITY_SCORE', 'AFFORDABILITY_SCORE', 'MARKET_SPEED_SCORE']].head(10)

# COMMAND ----------

# Weight each factor (similar to Niche)
# You can adjust these weights
WEIGHTS = {
    'INCOME_SCORE': 0.25,        # 25%
    'EDUCATION_SCORE': 0.20,     # 20%
    'DIVERSITY_SCORE': 0.15,     # 15%
    'AFFORDABILITY_SCORE': 0.25, # 25%
    'MARKET_SPEED_SCORE': 0.15   # 15%
}

# Calculate overall score
ranking_df['OVERALL_SCORE'] = (
    ranking_df['INCOME_SCORE'] * WEIGHTS['INCOME_SCORE'] +
    ranking_df['EDUCATION_SCORE'] * WEIGHTS['EDUCATION_SCORE'] +
    ranking_df['DIVERSITY_SCORE'] * WEIGHTS['DIVERSITY_SCORE'] +
    ranking_df['AFFORDABILITY_SCORE'] * WEIGHTS['AFFORDABILITY_SCORE'] +
    ranking_df['MARKET_SPEED_SCORE'] * WEIGHTS['MARKET_SPEED_SCORE']
)

# Create rank (1 = best)
ranking_df['RANK'] = ranking_df['OVERALL_SCORE'].rank(ascending=False).astype(int)

# Sort by rank
final_ranking = ranking_df.sort_values('RANK')

print("TOP 20 BEST PLACES TO LIVE IN DFW:")
final_ranking[['RANK', 'CITY', 'OVERALL_SCORE', 'POPULATION', 'MEDIAN_INCOME', 'AVG_SALE_PRICE']].head(20)

# COMMAND ----------

# Save ranking to Azure Storage
ranking_spark_df = spark.createDataFrame(final_ranking)

ranking_path = f"{path}rankings/dfw_best_places"
ranking_spark_df.write.format("delta").mode("overwrite").save(ranking_path)

print("Rankings saved!")
print("")
print("TOP 10 BEST PLACES TO LIVE IN DFW:")
print(final_ranking[['RANK', 'CITY', 'OVERALL_SCORE', 'MEDIAN_INCOME', 'AVG_SALE_PRICE', 'BACHELORS_PCT']].head(10).to_string(index=False))

# COMMAND ----------

# View bottom 10
print("BOTTOM 10:")
print(final_ranking[['RANK', 'CITY', 'OVERALL_SCORE', 'MEDIAN_INCOME', 'AVG_SALE_PRICE', 'BACHELORS_PCT']].tail(10).to_string(index=False))

# COMMAND ----------

# Remove cities with bad data
clean_df = combined_df[combined_df['MEDIAN_INCOME'] > 0].copy()

print(f"Removed bad data. {len(clean_df)} cities remaining.")

# Recalculate scores
clean_df['INCOME_SCORE'] = (clean_df['MEDIAN_INCOME'] - clean_df['MEDIAN_INCOME'].min()) / (clean_df['MEDIAN_INCOME'].max() - clean_df['MEDIAN_INCOME'].min()) * 100

clean_df['EDUCATION_SCORE'] = (clean_df['BACHELORS_PCT'] - clean_df['BACHELORS_PCT'].min()) / (clean_df['BACHELORS_PCT'].max() - clean_df['BACHELORS_PCT'].min()) * 100

clean_df['DIVERSITY_SCORE'] = (clean_df['DIVERSITY_PCT'] - clean_df['DIVERSITY_PCT'].min()) / (clean_df['DIVERSITY_PCT'].max() - clean_df['DIVERSITY_PCT'].min()) * 100

clean_df['AFFORDABILITY_SCORE'] = (1 - (clean_df['AVG_SALE_PRICE'] - clean_df['AVG_SALE_PRICE'].min()) / (clean_df['AVG_SALE_PRICE'].max() - clean_df['AVG_SALE_PRICE'].min())) * 100

clean_df['MARKET_SPEED_SCORE'] = (1 - (clean_df['AVG_DAYS_ON_MARKET'] - clean_df['AVG_DAYS_ON_MARKET'].min()) / (clean_df['AVG_DAYS_ON_MARKET'].max() - clean_df['AVG_DAYS_ON_MARKET'].min())) * 100

# New weights - reduce affordability penalty
WEIGHTS = {
    'INCOME_SCORE': 0.30,        # 30%
    'EDUCATION_SCORE': 0.25,     # 25%
    'DIVERSITY_SCORE': 0.15,     # 15%
    'AFFORDABILITY_SCORE': 0.15, # 15% (reduced)
    'MARKET_SPEED_SCORE': 0.15   # 15%
}

clean_df['OVERALL_SCORE'] = (
    clean_df['INCOME_SCORE'] * WEIGHTS['INCOME_SCORE'] +
    clean_df['EDUCATION_SCORE'] * WEIGHTS['EDUCATION_SCORE'] +
    clean_df['DIVERSITY_SCORE'] * WEIGHTS['DIVERSITY_SCORE'] +
    clean_df['AFFORDABILITY_SCORE'] * WEIGHTS['AFFORDABILITY_SCORE'] +
    clean_df['MARKET_SPEED_SCORE'] * WEIGHTS['MARKET_SPEED_SCORE']
)

clean_df['RANK'] = clean_df['OVERALL_SCORE'].rank(ascending=False).astype(int)

final_ranking = clean_df.sort_values('RANK')

print("")
print("TOP 20 BEST PLACES TO LIVE IN DFW (Fixed):")
print(final_ranking[['RANK', 'CITY', 'OVERALL_SCORE', 'MEDIAN_INCOME', 'AVG_SALE_PRICE', 'BACHELORS_PCT']].head(20).to_string(index=False))

# COMMAND ----------

# Save cleaned ranking to Azure Storage
ranking_spark_df = spark.createDataFrame(final_ranking)

ranking_path = f"{path}rankings/dfw_best_places"
ranking_spark_df.write.format("delta").mode("overwrite").save(ranking_path)

print("Final rankings saved!")

# COMMAND ----------

# Niche's actual 2024 Top 10 DFW suburbs (from their website)
niche_top_10 = ['Southlake', 'Coppell', 'Flower Mound', 'Frisco', 'Allen', 'Plano', 'McKinney', 'Richardson', 'Highland Village', 'Prosper']

# Check how many of Niche's top 10 are in your top 20
your_top_20 = final_ranking.head(20)['CITY'].tolist()

matches = [city for city in niche_top_10 if city in your_top_20]

print("COMPARISON TO NICHE:")
print(f"Niche Top 10: {niche_top_10}")
print(f"")
print(f"Your Top 20: {your_top_20}")
print(f"")
print(f"Matches: {len(matches)}/10 - {matches}")

# COMMAND ----------

# Check where the missing Niche cities ranked
missing = ['Southlake', 'McKinney', 'Richardson']

for city in missing:
    city_data = final_ranking[final_ranking['CITY'] == city]
    if len(city_data) > 0:
        print(f"{city}: Rank #{city_data['RANK'].values[0]}, Score: {city_data['OVERALL_SCORE'].values[0]:.1f}")
    else:
        print(f"{city}: Not in dataset")

# COMMAND ----------

# Check if Southlake exists in original data
print("In Census data:")
print(census_df[census_df['CITY'].str.contains('Southlake', case=False)]['CITY'].tolist())

print("\nIn Redfin data:")
print(redfin_df[redfin_df['CITY'].str.contains('Southlake', case=False)]['CITY'].tolist())

# COMMAND ----------

