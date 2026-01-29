USE RealEstateAnalytics;

-- Top 10 cities by property type (minimum 10 sales for reliability)
SELECT TOP 10
    CITY,
    PROPERTY_TYPE,
    YEAR,
    AVG_SALE_PRICE,
    AVG_PRICE_PER_SQFT,
    TOTAL_HOMES_SOLD
FROM vw_TexasMarketSummary
WHERE PROPERTY_TYPE = 'Single Family Residential'
    AND TOTAL_HOMES_SOLD >= 10
    AND YEAR = 2025
    AND AVG_SALE_PRICE IS NOT NULL
ORDER BY AVG_SALE_PRICE DESC;