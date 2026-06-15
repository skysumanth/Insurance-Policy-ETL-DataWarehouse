CREATE TABLE dbo.Stg_Policies(
 PolicyID INT,
 PolicyNumber VARCHAR(50),
 CustomerName VARCHAR(200),
 PolicyType VARCHAR(50),
 Premium DECIMAL(18,2),
 EffectiveDate DATETIME,
 ExpiryDate DATETIME,
 State VARCHAR(100),
 CreatedDate DATETIME,
 ModifiedDate DATETIME,
 LoadDate DATETIME DEFAULT GETDATE()
);