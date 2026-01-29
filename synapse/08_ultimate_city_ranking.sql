USE RealEstateAnalytics;

-- Ultimate DFW City Ranking: ALL Factors Combined
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
        AND CITY IN ('Dallas', 'Fort Worth', 'Plano', 'Irving', 'Arlington', 'Frisco', 'McKinney', 'Allen', 'Garland', 'Richardson', 'Carrollton', 'Grand Prairie', 'Mesquite', 'Lewisville', 'Flower Mound', 'Denton', 'The Colony', 'Coppell', 'Southlake', 'Grapevine', 'Cedar Hill', 'DeSoto', 'Duncanville', 'Farmers Branch', 'Rowlett', 'Wylie')
),
Appreciation AS (
    SELECT CITY, AVG_SALE_PRICE as Price_2020
    FROM vw_TexasMarketSummary
    WHERE PROPERTY_TYPE = 'Single Family Residential' AND YEAR = 2020
),
BLSData AS (
    SELECT AVG(UNEMPLOYMENT_RATE) as Avg_Unemployment_Rate
    FROM OPENROWSET(
        BULK 'bls/dfw_unemployment/',
        DATA_SOURCE = 'RealEstateData',
        FORMAT = 'DELTA'
    ) AS [result]
    WHERE YEAR = '2024'
),
MaxValues AS (
    SELECT MAX(Current_Price) as Max_Price, MAX(Days_On_Market) as Max_DOM, MAX(Sales_Volume) as Max_Volume
    FROM CurrentMetrics
)
SELECT TOP 20
    c.CITY,
    c.Current_Price,
    c.Days_On_Market,
    c.Sales_Volume,
    a.Price_2020,
    CASE WHEN a.Price_2020 > 0 THEN ROUND(((c.Current_Price - a.Price_2020) / a.Price_2020) * 100, 1) ELSE NULL END as Appreciation_Pct,
    b.Avg_Unemployment_Rate as DFW_Unemployment,
    (c.Current_Price / m.Max_Price) * 25 + (c.Days_On_Market / m.Max_DOM) * 20 + (1 - (c.Sales_Volume / m.Max_Volume)) * 15 + CASE WHEN a.Price_2020 > 0 THEN (1 - ((c.Current_Price - a.Price_2020) / a.Price_2020)) * 25 ELSE 25 END + (b.Avg_Unemployment_Rate / 10) * 15 as Ultimate_Score
FROM CurrentMetrics c
LEFT JOIN Appreciation a ON c.CITY = a.CITY
CROSS JOIN BLSData b
CROSS JOIN MaxValues m
WHERE a.Price_2020 IS NOT NULL
ORDER BY Ultimate_Score ASC;