import sqlite3
import os

# Check if database exists
print('Database exists:', os.path.exists('disease_history.db'))

# Connect to database
conn = sqlite3.connect('disease_history.db')
cursor = conn.cursor()

# Get table names
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print('Tables:', tables)

# Check if analysis_history table exists
cursor.execute("SELECT COUNT(*) FROM analysis_history")
count = cursor.fetchone()[0]
print('Number of records:', count)

# Get first few records
cursor.execute("SELECT * FROM analysis_history LIMIT 5")
records = cursor.fetchall()
print('Sample records:', records)

conn.close()