import sqlite3
import pandas as pd

# Load the merged data
data = pd.read_csv('merged_data.csv')

# Create a connection to the SQLite database
# (This will create the database file if it doesn't exist)
conn = sqlite3.connect('food_demand.db')

# Save the data to a table named 'orders_data'
data.to_sql('orders_data', conn, if_exists='replace', index=False)

# Verify by fetching the first few rows
cursor = conn.cursor()
cursor.execute("SELECT * FROM orders_data LIMIT 5;")
rows = cursor.fetchall()

# Print confirmation and a sample of the rows
print("Database 'food_demand.db' created and table 'orders_data' populated.")
for row in rows:
    print(row)

# Close the connection
conn.close()
