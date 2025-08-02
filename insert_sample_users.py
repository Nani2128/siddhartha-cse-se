import sqlite3

conn = sqlite3.connect("sits.db")
cursor = conn.cursor()

# Sample student
cursor.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)",
               ('23TQ1A5601', '123456', 'student'))

# Sample admin
cursor.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)",
               ('23TQ1A5661', 'admin123', 'admin'))

conn.commit()
conn.close()
print("✅ Sample users inserted.")
