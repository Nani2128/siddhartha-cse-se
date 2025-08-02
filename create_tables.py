import sqlite3

conn = sqlite3.connect("sits.db")
cursor = conn.cursor()

# Create users table (students + admins)
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT CHECK(role IN ('student', 'admin')) NOT NULL
)
''')

# Create posts table
cursor.execute('''
CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT,
    filename TEXT,
    uploaded_by TEXT,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
    approved INTEGER DEFAULT 1
)
''')

# Create attendance table
cursor.execute('''
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    date TEXT NOT NULL,
    status TEXT CHECK(status IN ('present', 'absent')) NOT NULL
)
''')

# Create student profiles table
cursor.execute('''
CREATE TABLE IF NOT EXISTS profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT UNIQUE NOT NULL,
    name TEXT,
    semester TEXT,
    branch TEXT,
    contact TEXT
)
''')

conn.commit()
conn.close()

print("✅ All required tables created successfully.")
