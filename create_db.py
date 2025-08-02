# create_db.py

import sqlite3
import os

def create_database():
    if os.path.exists("database.db"):
        os.remove("database.db")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT,
            name TEXT,
            dob TEXT,
            course TEXT,
            aadhar TEXT,
            ssc_marks TEXT,
            inter_marks TEXT,
            attendance INTEGER DEFAULT 0,
            total_days INTEGER DEFAULT 0,
            present_days INTEGER DEFAULT 0
        )
    ''')

    cursor.execute('''
        CREATE TABLE posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            content TEXT,
            filepath TEXT,
            filetype TEXT,
            category TEXT,
            timestamp TEXT,
            uploaded_at TEXT,
            approved INTEGER DEFAULT 0
        )
    ''')

    cursor.execute('''
        CREATE TABLE likes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER,
            username TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER,
            username TEXT,
            comment TEXT,
            timestamp TEXT
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ Database created successfully.")

if __name__ == "__main__":
    create_database()
