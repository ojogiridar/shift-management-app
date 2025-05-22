from flask import Flask, render_template, request, redirect, session, url_for, flash
import sqlite3
from pathlib import Path

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# 仮のユーザー情報（デモ用）
users = {
    'testuser': {'password': 'testpass', 'role': 'staff'},  # アルバイト
    'manager': {'password': 'adminpass', 'role': 'manager'} # 店長
}

# DBファイルのパス
DB_PATH = 'shifts.db'

# 初回のみDBを作成
def init_db():
    if not Path(DB_PATH).exists():
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute('''
                CREATE TABLE shifts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user TEXT NOT NULL,
                    date TEXT NOT NULL,
                    start TEXT NOT NULL,
                    end TEXT NOT NULL
                )
            ''')

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form['username']
        pw = request.form['password']
        user = users.get(name)
        if user and user['password'] == pw:
            session['username'] = name
            session['role'] = user['role']
            return redirect(url_for('dashboard'))
        return "ログイン失敗"

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    return render_template('dashboard.html', name=session['username'], role=session['role'])

@app.route('/submit_shift', methods=['GET', 'POST'])
def submit_shift():
    if 'username' not in session:
        return redirect(url_for('login'))

    if session['role'] != 'staff':
        return "許可されていないアクセスです", 403

    if request.method == 'POST':
        date = request.form['date']
        start = request.form['start']
        end = request.form['end']

        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                'INSERT INTO shifts (user, date, start, end) VALUES (?, ?, ?, ?)',
                (session['username'], date, start, end)
            )

        flash("シフトを提出しました！")
        return redirect(url_for('dashboard'))

    return render_template('submit_shift.html')

@app.route('/my_shifts')
def my_shifts():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']

    # 自分のシフトを取得（ID付き）
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(
            'SELECT id, date, start, end FROM shifts WHERE user = ? ORDER BY date',
            (username,)
        )
        shifts = cursor.fetchall()

    return render_template('my_shifts.html', name=username, shifts=shifts)

@app.route('/edit_shift/<int:shift_id>', methods=['GET', 'POST'])
def edit_shift(shift_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']

    if request.method == 'POST':
        date = request.form['date']
        start = request.form['start']
        end = request.form['end']

        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                'UPDATE shifts SET date = ?, start = ?, end = ? WHERE id = ? AND user = ?',
                (date, start, end, shift_id, username)
            )
        return redirect(url_for('my_shifts'))

    # 編集前のデータを取得
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(
            'SELECT * FROM shifts WHERE id = ? AND user = ?',
            (shift_id, username)
        )
        shift = cursor.fetchone()

    if shift is None:
        return "対象のシフトが見つかりません", 404

    return render_template('edit_shift.html', shift=shift)

@app.route('/delete_shift/<int:shift_id>')
def delete_shift(shift_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            'DELETE FROM shifts WHERE id = ? AND user = ?',
            (shift_id, username)
        )

    return redirect(url_for('my_shifts'))

@app.route('/all_shifts')
def all_shifts():
    if 'username' not in session:
        return redirect(url_for('login'))

    if session['role'] != 'manager':
        return "許可されていないアクセスです", 403

    # 全ユーザーのシフトを取得
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(
            'SELECT user, date, start, end FROM shifts ORDER BY date, start'
        )
        shifts = cursor.fetchall()

    return render_template('all_shifts.html', shifts=shifts)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
