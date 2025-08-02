from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
import sqlite3
import os
import re
from datetime import datetime

import pandas as pd

app = Flask(__name__)
app.secret_key = 'super-secret-key'
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def get_db():
    conn = sqlite3.connect('database.db', timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_column_exists():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(users)")
    columns = [row[1] for row in cursor.fetchall()]
    if 'attendance' not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN attendance INTEGER DEFAULT 0")
    if 'total_days' not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN total_days INTEGER DEFAULT 0")
    if 'present_days' not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN present_days INTEGER DEFAULT 0")
    cursor.execute("PRAGMA table_info(posts)")
    post_columns = [row[1] for row in cursor.fetchall()]
    if 'uploaded_at' not in post_columns:
        cursor.execute("ALTER TABLE posts ADD COLUMN uploaded_at TEXT")
    conn.commit()
    conn.close()


def init_db():
    if os.path.exists("database.db"):
        os.remove("database.db")
    conn = get_db()
    conn.execute('''
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
    conn.execute('''
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
    conn.execute('''
        CREATE TABLE likes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER,
            username TEXT
        )
    ''')
    conn.execute('''
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


@app.route('/')
def index():
    return render_template('index.html', current_year=datetime.now().year)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].upper()
        password = request.form['password']
        if not re.match(r'^23TQ1A56[0-9]{2}$', username):
            flash('❌ Invalid Roll Number Format!', 'error')
            return redirect(url_for('register'))
        user_num = int(username[-2:])
        if not (1 <= user_num <= 99):
            flash('❌ Roll number not allowed!', 'error')
            return redirect(url_for('register'))
        if user_num <= 62:
            role = 'student'
        else:
            role = 'admin'
            if password != 'SITS@2027':
                flash('❌ Incorrect Admin Password!', 'error')
                return redirect(url_for('register'))
        try:
            conn = get_db()
            conn.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
            conn.commit()
            flash('✅ Registered Successfully. Please Login.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('⚠️ Username already exists.', 'error')
            return redirect(url_for('register'))
    return render_template('register.html', current_year=datetime.now().year)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].upper()
        password = request.form['password']
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password)).fetchone()
        conn.close()
        if user:
            session['username'] = user['username']
            session['role'] = user['role']
            return redirect(url_for('admin_dashboard' if user['role'] == 'admin' else 'student_dashboard'))
        else:
            flash('❌ Invalid credentials.', 'error')
            return redirect(url_for('login'))
    return render_template('login.html', current_year=datetime.now().year)


@app.route('/student_dashboard')
def student_dashboard():
    if 'username' not in session or session['role'] != 'student':
        return redirect(url_for('login'))
    return render_template('student_dashboard.html', username=session['username'])


@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    username = session['username']
    role = session['role']
    category_filter = request.args.get('category', '')
    query = request.args.get('q', '')
    if query:
        posts = conn.execute('''
            SELECT * FROM posts 
            WHERE approved=1 AND 
            (username LIKE ? OR content LIKE ? OR category LIKE ?)
            ORDER BY id DESC
        ''', (f"%{query}%", f"%{query}%", f"%{query}%")).fetchall()
    elif category_filter:
        posts = conn.execute("SELECT * FROM posts WHERE approved=1 AND category=? ORDER BY id DESC",
                             (category_filter,)).fetchall()
    else:
        posts = conn.execute("SELECT * FROM posts WHERE approved=1 ORDER BY id DESC").fetchall()
    conn.close()
    return render_template('dashboard.html', username=username, role=role,
                           posts=posts, query=query, selected_category=category_filter,
                           current_year=datetime.now().year)


@app.route('/upload_post', methods=['GET', 'POST'])
def upload_post():
    if 'username' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    ensure_column_exists()
    if request.method == 'POST':
        content = request.form['content']
        category = request.form.get('category', 'general').lower()
        file = request.files.get('file')
        filepath = ''
        ext = ''
        if file and file.filename:
            ext = file.filename.rsplit('.', 1)[-1].lower()
            filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            filepath = filepath.replace('\\', '/')
        conn = get_db()
        conn.execute('''
            INSERT INTO posts (username, content, filepath, filetype, category, timestamp, uploaded_at, approved)
            VALUES (?, ?, ?, ?, ?, datetime('now'), datetime('now'), 1)
        ''', (session['username'], content, filepath, ext, category))
        conn.commit()
        conn.close()
        flash('✅ Post uploaded successfully!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('upload.html', current_year=datetime.now().year)


@app.route('/admin_dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    ensure_column_exists()
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM posts ORDER BY uploaded_at DESC")
    posts = cur.fetchall()
    cur.execute("SELECT * FROM users WHERE role = 'student'")
    students = cur.fetchall()
    conn.close()
    category_posts = {}
    for post in posts:
        category = post['category']
        if category not in category_posts:
            category_posts[category] = []
        category_posts[category].append(post)
    return render_template('admin_dashboard.html',
                           username=session['username'],
                           posts=posts,
                           students=students,
                           category_posts=category_posts)


@app.route('/approve_post/<int:post_id>', methods=['POST'])
def approve_post(post_id):
    if 'username' not in session or session['role'] != 'admin':
        flash('❌ Unauthorized action.', 'error')
        return redirect(url_for('login'))
    conn = get_db()
    conn.execute("UPDATE posts SET approved = 1 WHERE id = ?", (post_id,))
    conn.commit()
    conn.close()
    flash('✅ Post approved successfully!')
    return redirect(url_for('admin_dashboard'))


@app.route('/reject_post/<int:post_id>', methods=['POST'])
def reject_post(post_id):
    if 'username' not in session or session['role'] != 'admin':
        flash('❌ Unauthorized action.', 'error')
        return redirect(url_for('login'))
    conn = get_db()
    conn.execute("UPDATE posts SET approved = -1 WHERE id = ?", (post_id,))
    conn.commit()
    conn.close()
    flash('❌ Post rejected.')
    return redirect(url_for('admin_dashboard'))


@app.route('/like/<int:post_id>')
def like_post(post_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    username = session['username']
    already = conn.execute("SELECT * FROM likes WHERE post_id=? AND username=?", (post_id, username)).fetchone()
    if not already:
        conn.execute("INSERT INTO likes (post_id, username) VALUES (?, ?)", (post_id, username))
        conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))


@app.route('/comment/<int:post_id>', methods=['POST'])
def comment_post(post_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    comment = request.form['comment']
    conn = get_db()
    conn.execute("INSERT INTO comments (post_id, username, comment, timestamp) VALUES (?, ?, ?, datetime('now'))",
                 (post_id, session['username'], comment))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))


@app.route('/profile')
def profile():
    if 'username' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE username = ?", (session['username'],)).fetchone()
    conn.close()
    return render_template("profile.html", user=user, current_year=datetime.now().year)


@app.route('/attendance')
def attendance():
    if 'username' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE username=?", (session['username'],)).fetchone()
    conn.close()
    return render_template('attendance.html', user=user)


@app.route('/student_profiles')
def student_profiles():
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT username AS roll_number, name, course, dob, aadhar, ssc_marks, inter_marks, attendance, total_days, present_days 
        FROM users
        WHERE role = 'student'
          AND username BETWEEN '23TQ1A5601' AND '23TQ1A5662'
        ORDER BY username
    """)
    students = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('all_profiles.html', students=students, current_year=datetime.now().year)


@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if 'username' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    if request.method == 'POST':
        roll = request.form['roll_number'].upper()
        name = request.form['name']
        course = request.form['course']
        dob = request.form['dob']
        aadhar = request.form['aadhar']
        ssc = request.form['ssc_marks']
        inter = request.form['inter_marks']
        attendance = int(request.form['attendance'])
        total_days = int(request.form['total_days'])
        present_days = int(request.form['present_days'])

        conn = get_db()
        cursor = conn.cursor()

        # Check if student already exists
        existing = cursor.execute("SELECT * FROM users WHERE username = ?", (roll,)).fetchone()

        if existing:
            # Update existing student details
            cursor.execute("""
                UPDATE users
                SET name=?, dob=?, course=?, aadhar=?, ssc_marks=?, inter_marks=?, attendance=?, total_days=?, present_days=?
                WHERE username=?
            """, (name, dob, course, aadhar, ssc, inter, attendance, total_days, present_days, roll))
            flash(f"✅ Student {name}'s profile updated successfully!", "success")
        else:
            # Insert new student
            cursor.execute("""
                INSERT INTO users (username, password, role, name, dob, course, aadhar, ssc_marks, inter_marks, attendance, total_days, present_days)
                VALUES (?, ?, 'student', ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (roll, roll, name, dob, course, aadhar, ssc, inter, attendance, total_days, present_days))
            flash(f"✅ Student {name} added successfully!", "success")

        conn.commit()
        conn.close()
        return redirect(url_for('student_profiles'))

    return render_template('add_student.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('🔓 Logged out.', 'info')
    return redirect(url_for('login'))


@app.route('/delete/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    conn = get_db()
    conn.execute('DELETE FROM posts WHERE id = ?', (post_id,))
    conn.commit()
    conn.close()
    flash('Post deleted successfully!')
    return redirect(url_for('admin_dashboard'))


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
