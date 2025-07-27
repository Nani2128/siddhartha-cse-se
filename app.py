from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import re
import os

app = Flask(__name__)
app.secret_key = 'super-secret-key'  # Replace with env var in production

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

DATABASE = os.path.join(os.getcwd(), 'database.db')

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            content TEXT,
            filepath TEXT,
            filetype TEXT,
            category TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

@app.before_first_request
def initialize():
    init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].upper()
        password = request.form['password']

        if not re.match(r'^23TQ1A56[0-9]{2}$', username):
            flash('❌ Invalid Username Format!', 'error')
            return redirect(url_for('register'))

        user_num = int(username[-2:])
        if not (1 <= user_num <= 99):
            flash('❌ Username not allowed!', 'error')
            return redirect(url_for('register'))

        role = 'student' if user_num <= 60 else 'admin'

        try:
            conn = get_db()
            conn.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                         (username, password, role))
            conn.commit()
            flash('✅ Registered Successfully. Please Login.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('⚠️ Username already exists.', 'error')
            return redirect(url_for('register'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].upper()
        password = request.form['password']

        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE username=? AND password=?", 
                            (username, password)).fetchone()

        if user:
            session['username'] = user['username']
            session['role'] = user['role']
            flash('✅ Login successful', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('❌ Invalid credentials.', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    role = session['role']

    if role == 'admin' and request.method == 'POST':
        content = request.form['content']
        file = request.files.get('file')
        category = request.form['category']

        filepath = ''
        ext = ''
        if file and file.filename:
            ext = file.filename.rsplit('.', 1)[-1].lower()
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)

        conn = get_db()
        conn.execute('''
            INSERT INTO posts (username, content, filepath, filetype, category, timestamp)
            VALUES (?, ?, ?, ?, ?, datetime('now'))
        ''', (username, content, filepath, ext, category))
        conn.commit()
        flash('📤 Post uploaded.', 'success')

    conn = get_db()
    posts = conn.execute("SELECT * FROM posts ORDER BY id DESC").fetchall()
    return render_template('dashboard.html', username=username, role=role, posts=posts)

@app.route('/logout')
def logout():
    session.clear()
    flash('🔓 Logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/delete/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    if session.get('role') != 'admin':
        flash('❌ Unauthorized', 'error')
        return redirect(url_for('dashboard'))

    conn = get_db()
    conn.execute("DELETE FROM posts WHERE id=?", (post_id,))
    conn.commit()
    flash('🗑️ Post deleted.', 'success')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
