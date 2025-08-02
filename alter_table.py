import sqlite3

conn = sqlite3.connect("sits.db")  # Make sure this file exists in the current folder
conn.execute("ALTER TABLE posts ADD COLUMN approved INTEGER DEFAULT 1")
conn.commit()
conn.close()

print("✅ Column 'approved' added successfully to 'posts' table.")
