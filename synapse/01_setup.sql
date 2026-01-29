-- Create a database to organize your views
CREATE DATABASE RealEstateAnalytics;
GO

USE RealEstateAnalytics;
GO

-- Recreate your credential and data source in this database
CREATE MASTER KEY ENCRYPTION BY PASSWORD = 'YOUR_STRONG_PASSWORD_HERE';
GO

CREATE DATABASE SCOPED CREDENTIAL SynapseIdentity
WITH IDENTITY = 'Managed Identity';
GO

CREATE EXTERNAL DATA SOURCE RealEstateData
WITH (
    LOCATION = 'https://strealestatedatalinh.blob.core.windows.net/raw-data',
    CREDENTIAL = SynapseIdentity
);
GO

-- Now create a view for easy querying
CREATE VIEW vw_TexasMarketSummary AS
SELECT *
FROM OPENROWSET(
    BULK 'gold/texas_market_summary/',
    DATA_SOURCE = 'RealEstateData',
    FORMAT = 'DELTA'
) AS [result];
GO

-- Test it
SELECT TOP 10 * FROM vw_TexasMarketSummary;
