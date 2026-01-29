USE RealEstateAnalytics;

-- Top 10 most expensive cities (Single Family Residential, most recent year)
WITH LatestYear AS (
    SELECT MAX(YEAR) as MaxYear FROM vw_TexasMarketSummary
)
SELECT TOP 10
    CITY,
    YEAR,
    AVG_SALE_PRICE,
    AVG_PRICE_PER_SQFT,
    TOTAL_HOMES_SOLD
FROM vw_TexasMarketSummary
WHERE PROPERTY_TYPE = 'Single Family Residential'
    AND YEAR = (SELECT MaxYear FROM LatestYear)
    AND AVG_SALE_PRICE IS NOT NULL
ORDER BY AVG_SALE_PRICE DESC;