USE RealEstateAnalytics;

-- Highest & lowest avg sale price by property type
SELECT 
    PROPERTY_TYPE,
    MAX(AVG_SALE_PRICE) as HighestAvgPrice,
    MIN(AVG_SALE_PRICE) as LowestAvgPrice,
    AVG(AVG_SALE_PRICE) as OverallAvgPrice,
    COUNT(*) as TotalRecords
FROM vw_TexasMarketSummary
WHERE AVG_SALE_PRICE IS NOT NULL
GROUP BY PROPERTY_TYPE
ORDER BY HighestAvgPrice DESC;