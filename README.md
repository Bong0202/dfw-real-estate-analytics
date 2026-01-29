# dfw-real-estate-analytics
End-to-end Azure data engineering project with Databricks, Synapse, and Power BI 

# DFW Real Estate Analytics Platform

An end-to-end Azure data engineering project that analyzes Dallas-Fort Worth real estate market trends, combining multiple data sources to create city rankings and interactive dashboards.

## Architecture
```
Data Sources → Azure Data Factory → Databricks → Synapse Analytics → Power BI
                                        ↓
                              Census API + BLS API
```

## Data Sources

| Source | Data | Type |
|--------|------|------|
| **Redfin** | Home prices, days on market, inventory | CSV/TSV |
| **Census API** | Income, education, diversity, population | REST API |
| **BLS API** | Unemployment rates | REST API |

## Technologies Used

- **Azure Data Factory** - Pipeline orchestration
- **Azure Databricks** - Data transformation (PySpark)
- **Azure Synapse Analytics** - SQL data warehouse
- **Power BI** - Interactive dashboards
- **Delta Lake** - Data storage format
- **Python** - API integration

## Project Structure
```
github_files/
├── databricks/
│   ├── 00_setup.py          (key replaced with placeholder)
│   ├── 01_redfin_pipeline.py
│   ├── 02_census_data.py    (key replaced with placeholder)
│   ├── 03_bls_data.py
│   └── 04_combine_rankings.py
├── synapse/
│   ├── 01_setup.sql         (password replaced with placeholder)
│   ├── 02_price_ranges_by_property_type.sql
│   ├── 03_extreme_prices_analysis.sql
│   ├── 04_top_10_expensive_cities.sql
│   ├── 05_top_cities_2025.sql
│   ├── 06_deal_score_hot_markets.sql
│   ├── 07_best_investment_cities.sql
│   └── 08_ultimate_city_ranking.sql
├── adf/
│   └── adf_pipeline.json
└── powerbi/
    └── DFW_RealEstate_Dashboard.pbix
```

## Data Pipeline

### Medallion Architecture
- **Bronze Layer**: Raw data ingestion from Redfin
- **Silver Layer**: Cleaned and transformed data
- **Gold Layer**: Aggregated analytics-ready data

### Key Transformations
- Filtered Texas cities from national dataset
- Converted date formats and handled null values
- Calculated year-over-year price changes
- Created city rankings with weighted scoring

## Key Insights

### Top 10 Most Expensive DFW Cities (2025)
1. Highland Park
2. Westlake
3. University Park
4. Piney Point Village
5. Southlake

### Best Investment Cities (Price + Appreciation + Jobs)
1. Fort Worth - $335K avg, 35% appreciation
2. Duncanville - $304K avg, 49% appreciation
3. Grand Prairie - $351K avg, 39% appreciation

### City Rankings vs Niche.com
- **70% accuracy** matching Niche's top 10 DFW cities
- Using only 3 data sources (Redfin, Census, BLS)

## SQL Skills Demonstrated

- Window Functions (ROW_NUMBER, LAG, RANK)
- Common Table Expressions (CTEs)
- Complex JOINs (LEFT, CROSS)
- Aggregations and GROUP BY
- Subqueries and derived tables

## Power BI Dashboard

Features:
- Bar chart: Top cities by average sale price
- Line chart: Price trends over time (2018-2025)
- Slicer: Filter by property type
- Table: Detailed city metrics
- Cards: Key metrics (total homes sold, average price)

## How to Run

### Prerequisites
- Azure subscription
- Databricks workspace
- Synapse Analytics workspace
- Power BI Desktop

### Steps
1. Clone this repository
2. Set up Azure resources (Storage, Databricks, Synapse)
3. Run Databricks notebooks in order (00 → 04)
4. Execute Synapse SQL scripts
5. Open Power BI and connect to Synapse

## Contact

**Linh Nguyen**
- LinkedIn: https://www.linkedin.com/in/linhnguyen0202/
- Email: linhdada22@gmail.com
