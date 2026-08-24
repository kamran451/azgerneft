import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory

app = Flask(__name__)
app.secret_key = 'azgerneft_xususi_gizli_acar_2026'

# Admin şifrəniz
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', '5847039k')

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

# Service Worker faylının xidmət edilməsi (Offline işləmək üçün)
@app.route('/sw.js')
def service_worker():
    return send_from_directory('static', 'sw.js')

@app.route('/')
def index():
    query = request.args.get('query', '').strip()
    conn = get_db()
    if query:
        quyular = conn.execute('SELECT * FROM quyular WHERE quyu_no LIKE ? ORDER BY quyu_no ASC', (f'%{query}%',)).fetchall()
    else:
        quyular = conn.execute('SELECT * FROM quyular ORDER BY quyu_no ASC').fetchall()
    conn.close()
            
    return render_template('index.html', quyular=quyular, query=query)

@app.route('/api/quyular')
def api_quyular():
    conn = get_db()
    quyular = conn.execute('SELECT * FROM quyular ORDER BY quyu_no ASC').fetchall()
    conn.close()
    return jsonify([dict(q) for q in quyular])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('admin'))
        else:
            return render_template('login.html', xeta="Şifrə yanlışdır!")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('index'))

@app.route('/admin')
def admin():
    if not session.get('admin'):
        return redirect(url_for('login'))
    
    axtaris = request.args.get('axtaris', '').strip()
    conn = get_db()
    if axtaris:
        quyular = conn.execute('SELECT * FROM quyular WHERE quyu_no LIKE ? ORDER BY quyu_no ASC', (f'%{axtaris}%',)).fetchall()
    else:
        quyular = conn.execute('SELECT * FROM quyular ORDER BY quyu_no ASC').fetchall()
    conn.close()
    
    return render_template('admin.html', quyular=quyular, axtaris=axtaris)

@app.route('/elave-et', methods=['POST'])
def elave_et():
    if not session.get('admin'):
        return redirect(url_for('login'))
    
    quyu_no = request.form.get('quyu_no').strip()
    lat = request.form.get('lat')
    lon = request.form.get('lon')
    qeyd = request.form.get('qeyd')
    
    try:
        conn = get_db()
        conn.execute('INSERT INTO quyular (quyu_no, lat, lon, qeyd) VALUES (?, ?, ?, ?)',
                     (quyu_no, float(lat), float(lon), qeyd))
        conn.commit()
        conn.close()
    except Exception as e:
        pass
        
    return redirect(url_for('admin'))

@app.route('/duzelis/<int:id>', methods=['POST'])
def duzelis(id):
    if not session.get('admin'):
        return redirect(url_for('login'))
    
    quyu_no = request.form.get('quyu_no').strip()
    lat = request.form.get('lat')
    lon = request.form.get('lon')
    qeyd = request.form.get('qeyd')
    
    try:
        conn = get_db()
        conn.execute('UPDATE quyular SET quyu_no = ?, lat = ?, lon = ?, qeyd = ? WHERE id = ?',
                     (quyu_no, float(lat), float(lon), qeyd, id))
        conn.commit()
        conn.close()
    except Exception as e:
        pass

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
