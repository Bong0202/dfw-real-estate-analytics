USE RealEstateAnalytics;

-- Find cities with lowest prices, shortest days on market, and highest sales volume
-- (Good indicators for hot markets with deals)

SELECT TOP 20
    CITY,
    YEAR,
    PROPERTY_TYPE,
    AVG_SALE_PRICE,
    AVG_DAYS_ON_MARKET,
    TOTAL_HOMES_SOLD,
    AVG_PRICE_PER_SQFT,
    -- Create a "deal score" - lower is better
    -- Normalize each metric to give equal weight
    (AVG_SALE_PRICE / 1000000.0) + -- Cheaper is better (lower score)
    (AVG_DAYS_ON_MARKET / 100.0) - -- Faster sales is better (lower score)
    (TOTAL_HOMES_SOLD / 100.0) as DealScore -- Higher volume is better (subtract to lower score)
FROM vw_TexasMarketSummary
WHERE PROPERTY_TYPE = 'Single Family Residential'
    AND YEAR = 2025
    AND TOTAL_HOMES_SOLD >= 20  -- Require minimum volume for reliability
    AND AVG_DAYS_ON_MARKET IS NOT NULL
    AND AVG_SALE_PRICE IS NOT NULL
ORDER BY DealScore ASC;  -- Lower score = better deal