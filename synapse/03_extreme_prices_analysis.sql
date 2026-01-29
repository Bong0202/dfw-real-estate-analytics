USE RealEstateAnalytics;

-- Find the actual cities with highest and lowest prices for each property type

-- HIGHEST PRICES
SELECT 
    'HIGHEST' as PriceCategory,
    PROPERTY_TYPE,
    CITY,
    YEAR,
    AVG_SALE_PRICE,
    TOTAL_HOMES_SOLD
FROM (
    SELECT 
        PROPERTY_TYPE,
        CITY,
        YEAR,
        AVG_SALE_PRICE,
        TOTAL_HOMES_SOLD,
        ROW_NUMBER() OVER (PARTITION BY PROPERTY_TYPE ORDER BY AVG_SALE_PRICE DESC) as rn
    FROM vw_TexasMarketSummary
    WHERE AVG_SALE_PRICE IS NOT NULL
) ranked
WHERE rn = 1

UNION ALL

-- LOWEST PRICES
SELECT 
    'LOWEST' as PriceCategory,
    PROPERTY_TYPE,
    CITY,
    YEAR,
    AVG_SALE_PRICE,
    TOTAL_HOMES_SOLD
FROM (
    SELECT 
        PROPERTY_TYPE,
        CITY,
        YEAR,
        AVG_SALE_PRICE,
        TOTAL_HOMES_SOLD,
        ROW_NUMBER() OVER (PARTITION BY PROPERTY_TYPE ORDER BY AVG_SALE_PRICE ASC) as rn
    FROM vw_TexasMarketSummary
    WHERE AVG_SALE_PRICE IS NOT NULL
) ranked
WHERE rn = 1

ORDER BY PriceCategory DESC, PROPERTY_TYPE;