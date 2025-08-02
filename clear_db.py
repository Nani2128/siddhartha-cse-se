import sqlite3

def delete_all_data():
    # Connect to the exact same database file created by create_db.py
    conn = sqlite3.connect('database.db')  # Make sure this path matches create_db.py
    cursor = conn.cursor()
    tables = ['users', 'posts', 'likes', 'comments']
    for table in tables:
        cursor.execute(f"DELETE FROM {table};")
    conn.commit()
    conn.close()
    print("All user data deleted successfully.")

if __name__ == "__main__":
    delete_all_data()
