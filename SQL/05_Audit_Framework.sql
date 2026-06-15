CREATE TABLE dbo.ETL_Run_History(
 RunID INT IDENTITY(1,1) PRIMARY KEY,
 PackageName VARCHAR(100),
 StartTime DATETIME,
 EndTime DATETIME,
 RecordsExtracted INT,
 RecordsLoaded INT,
 RecordsRejected INT,
 Status VARCHAR(50)
);