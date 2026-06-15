import pyodbc

conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost\\MSSQLSERVER01;"
    "DATABASE=InsurancePortalDB;"
    "Trusted_Connection=yes;"
)

print("Connection Successful!")

cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM Policies")

print("Total Policies:", cursor.fetchone()[0])

conn.close()