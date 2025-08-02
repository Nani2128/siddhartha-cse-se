import sqlite3

# Path to your database file
db_path = 'database.db'

try:
    conn = sqlite3.connect(db_path, timeout=10)
    cursor = conn.cursor()

    # Add 'approved' column if not already exists
    try:
        cursor.execute("ALTER TABLE posts ADD COLUMN approved INTEGER DEFAULT 0")
        print("✅ Column 'approved' added to posts table.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("⚠️ Column 'approved' already exists.")
        else:
            raise e

    conn.commit()
    conn.close()

except sqlite3.OperationalError as e:
    print("❌ Database is locked. Make sure no Flask app or DB viewer is using it.")
    print("Error:", e)
