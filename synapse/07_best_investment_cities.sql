USE RealEstateAnalytics;

-- Best Investment Cities in DFW: Price + Appreciation + Low Unemployment
WITH CurrentMetrics AS (
    SELECT 
        CITY,
        AVG_SALE_PRICE as Current_Price,
        AVG_DAYS_ON_MARKET as Days_On_Market,
        TOTAL_HOMES_SOLD as Sales_Volume
    FROM vw_TexasMarketSummary
    WHERE PROPERTY_TYPE = 'Single Family Residential'
        AND YEAR = 2025
        AND TOTAL_HOMES_SOLD >= 50
        -- DFW metro cities only
        AND CITY IN ('Dallas', 'Fort Worth', 'Plano', 'Irving', 'Arlington', 'Frisco', 
                     'McKinney', 'Allen', 'Garland', 'Richardson', 'Carrollton', 
                     'Grand Prairie', 'Mesquite', 'Lewisville', 'Flower Mound', 'Denton', 
                     'The Colony', 'Coppell', 'Southlake', 'Grapevine', 'Cedar Hill',
                     'DeSoto', 'Duncanville', 'Farmers Branch', 'Rowlett', 'Wylie')
),
Appreciation AS (
    SELECT 
        CITY,
        AVG_SALE_PRICE as Price_2020
    FROM vw_TexasMarketSummary
    WHERE PROPERTY_TYPE = 'Single Family Residential'
        AND YEAR = 2020
),
BLSData AS (
    SELECT 
        YEAR,
        AVG(UNEMPLOYMENT_RATE) as Avg_Unemployment_Rate
    FROM OPENROWSET(
        BULK 'bls/dfw_unemployment/',
        DATA_SOURCE = 'RealEstateData',
        FORMAT = 'DELTA'
    ) AS [result]
    WHERE YEAR = 2024  -- Most recent full year
    GROUP BY YEAR
)
SELECT TOP 20
    c.CITY,
    c.Current_Price,
    c.Days_On_Market,
    c.Sales_Volume,
    a.Price_2020,
    b.Avg_Unemployment_Rate as DFW_Unemployment_Rate,
    -- Calculate appreciation
    CASE 
        WHEN a.Price_2020 > 0 
        THEN ((c.Current_Price - a.Price_2020) / a.Price_2020) * 100
        ELSE NULL
    END as Five_Year_Appreciation_Pct,
    -- Annualized return
    CASE 
        WHEN a.Price_2020 > 0 
        THEN (POWER(c.Current_Price / a.Price_2020, 1.0/5.0) - 1) * 100
        ELSE NULL
    END as Annualized_Return_Pct,
    -- Investment score (lower price is better, higher appreciation is better, lower unemployment is better)
    (c.Current_Price / 100000.0) * 0.3 +  -- 30% weight on affordability (lower is better)
    (100 - CASE WHEN a.Price_2020 > 0 THEN (POWER(c.Current_Price / a.Price_2020, 1.0/5.0) - 1) * 100 ELSE 0 END) * 0.5 +  -- 50% weight on appreciation (invert so lower score = higher appreciation)
    (b.Avg_Unemployment_Rate) * 0.2  -- 20% weight on unemployment (lower is better)
    as Investment_Score
FROM CurrentMetrics c
LEFT JOIN Appreciation a ON c.CITY = a.CITY
CROSS JOIN BLSData b  -- DFW unemployment applies to all DFW cities
WHERE a.Price_2020 IS NOT NULL
    AND c.Current_Price < 600000  -- Affordable threshold
ORDER BY Investment_Score ASC;  -- Lower score = better investment