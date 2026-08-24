import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = 'azgerneft_gizli_acar_key'

def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS quyular (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quyu_no TEXT UNIQUE NOT NULL,
            lat REAL NOT NULL,
            lon REAL NOT NULL,
            qeyd TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    search_query = request.args.get('search', '').strip()
    conn = get_db()
    
    if search_query:
        wells = conn.execute(
            'SELECT * FROM quyular WHERE quyu_no LIKE ? ORDER BY quyu_no ASC', 
            (f'%{search_query}%',)
        ).fetchall()
    else:
        wells = conn.execute('SELECT * FROM quyular ORDER BY quyu_no ASC').fetchall()
        
    conn.close()
    return render_template('index.html', wells=wells, search=search_query)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Admin istifadəçi adı və şifrəsi
        if username == 'admin' and password == '123456':
            session['admin'] = True
            return redirect(url_for('admin'))
        else:
            error = 'İstifadəçi adı və ya şifrə yanlışdır!'
            
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('index'))

@app.route('/admin')
def admin():
    if not session.get('admin'):
        return redirect(url_for('login'))
    
    conn = get_db()
    wells = conn.execute('SELECT * FROM quyular ORDER BY quyu_no ASC').fetchall()
    conn.close()
    return render_template('admin.html', wells=wells)

@app.route('/elave-et', methods=['POST'])
def elave_et():
    if not session.get('admin'):
        return redirect(url_for('login'))
        
    quyu_no = request.form.get('quyu_no')
    lat = request.form.get('lat')
    lon = request.form.get('lon')
    qeyd = request.form.get('qeyd')
    
    conn = get_db()
    try:
        conn.execute('INSERT INTO quyular (quyu_no, lat, lon, qeyd) VALUES (?, ?, ?, ?)',
                     (quyu_no, float(lat), float(lon), qeyd))
        conn.commit()
    except Exception as e:
        print("Xəta:", e)
    finally:
        conn.close()
        
    return redirect(url_for('admin'))

@app.route('/sil/<int:id>', methods=['POST'])
def sil(id):
    if not session.get('admin'):
        return redirect(url_for('login'))
    
    conn = get_db()
    conn.execute('DELETE FROM quyular WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
