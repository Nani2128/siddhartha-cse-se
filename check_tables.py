# check_tables.py
import sqlite3

# Connect to your database file
conn = sqlite3.connect("sits.db")
cursor = conn.cursor()

# Query to list all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("📄 Tables in the database:")
for t in tables:
    print("-", t[0])

conn.close()
