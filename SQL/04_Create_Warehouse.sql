CREATE TABLE dbo.Rej_Policies(
 RejectID INT IDENTITY(1,1) PRIMARY KEY,
 PolicyID INT,
 PolicyNumber VARCHAR(50),
 CustomerName VARCHAR(200),
 PolicyType VARCHAR(50),
 Premium DECIMAL(18,2),
 EffectiveDate DATETIME,
 ExpiryDate DATETIME,
 State VARCHAR(100),
 RejectReason VARCHAR(500),
 RejectDate DATETIME DEFAULT GETDATE()
);

CREATE TABLE dbo.DimPolicyType(
 PolicyTypeKey INT IDENTITY(1,1) PRIMARY KEY,
 PolicyTypeName VARCHAR(50) UNIQUE
);

CREATE TABLE dbo.DimState(
 StateKey INT IDENTITY(1,1) PRIMARY KEY,
 StateName VARCHAR(100) UNIQUE
);

CREATE TABLE dbo.FactPolicy(
 FactPolicyKey INT IDENTITY(1,1) PRIMARY KEY,
 PolicyID INT,
 PolicyNumber VARCHAR(50),
 PolicyTypeKey INT,
 StateKey INT,
 Premium DECIMAL(18,2),
 EffectiveDate DATETIME,
 ExpiryDate DATETIME,
 CreatedDate DATETIME
);