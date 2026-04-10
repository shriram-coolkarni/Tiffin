from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import date

app = Flask(__name__)
app.secret_key = 'secret123'

DB = 'tiffin.db'

# ---------- DB SETUP ----------
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS tiffin (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        date TEXT,
        afternoon_count INTEGER,
        night_count INTEGER
    )''')

    conn.commit()
    conn.close()

init_db()

# ---------- ROUTES ----------
@app.route('/', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username,password))
        user = c.fetchone()
        conn.close()

        if user:
            session['user_id'] = user[0]
            return redirect('/dashboard')

    return render_template('login.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("INSERT INTO users (username,password) VALUES (?,?)", (username,password))
        conn.commit()
        conn.close()

        return redirect('/')

    return render_template('register.html')

@app.route('/dashboard', methods=['GET','POST'])
def dashboard():
    if 'user_id' not in session:
        return redirect('/')

    user_id = session['user_id']

    if request.method == 'POST':
        tiffin_date = request.form['date']
        afternoon = int(request.form['afternoon'])
        night = int(request.form['night'])

        conn = sqlite3.connect(DB)
        c = conn.cursor()

        c.execute("SELECT * FROM tiffin WHERE user_id=? AND date=?", (user_id,tiffin_date))
        existing = c.fetchone()

        if existing:
            c.execute("UPDATE tiffin SET afternoon_count=?, night_count=? WHERE id=?", (afternoon, night, existing[0]))
        else:
            c.execute("INSERT INTO tiffin (user_id,date,afternoon_count,night_count) VALUES (?,?,?,?)", (user_id,tiffin_date,afternoon,night))

        conn.commit()
        conn.close()

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT date,afternoon_count,night_count FROM tiffin WHERE user_id=? ORDER BY date DESC", (user_id,))
    records = c.fetchall()
    conn.close()

    # calculate totals
    total = 0
    for r in records:
        afternoon_total = r[1] * 60
        night_total = r[2] * 80
        total += afternoon_total + night_total

    return render_template('dashboard.html', records=records, today=str(date.today()), total=total)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
