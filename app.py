import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, jsonify

app = Flask(__name__)
app.secret_key = 'azgerneft_secret_key_2026'

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
            meden TEXT,
            sahe TEXT,
            telefon TEXT,
            qeyd TEXT
        )
    ''')
    conn.commit()

    count = conn.execute('SELECT COUNT(*) FROM quyular').fetchone()[0]
    if count == 0:
        sample_wells = [
            ('N70', 40.8500, 49.1200, '1-ci Mədən', 'Siyəzən sahəsi', '+994501234567', 'Nümunə quyu 1'),
            ('№1', 40.8550, 49.1250, '2-ci Mədən', 'Mərkəzi sahə', '+994509876543', 'Nümunə quyu 2')
        ]
        conn.executemany('''
            INSERT INTO quyular (quyu_no, lat, lon, meden, sahe, telefon, qeyd) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', sample_wells)
        conn.commit()
    conn.close()

init_db()

# Oflayn rejim üçün quyuları JSON formatında verən API
@app.route('/api/quyular')
def api_quyular():
    conn = get_db()
    wells = conn.execute('SELECT * FROM quyular ORDER BY id DESC').fetchall()
    conn.close()
    return jsonify([dict(w) for w in wells])

@app.route('/')
def index():
    conn = get_db()
    wells = conn.execute('SELECT * FROM quyular ORDER BY id DESC').fetchall()
    conn.close()
    return render_template('index.html', wells=wells)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        password = request.form.get('password')
        if password == '123' or password == '123456':
            session['admin'] = True
            return redirect(url_for('admin'))
        else:
            error = 'Giriş şifrəsi yanlışdır!'
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
    wells = conn.execute('SELECT * FROM quyular ORDER BY id DESC').fetchall()
    conn.close()
    return render_template('admin.html', wells=wells)

@app.route('/elave-et', methods=['POST'])
def elave_et():
    if not session.get('admin'):
        return redirect(url_for('login'))
    
    quyu_no = request.form.get('quyu_no')
    lat = request.form.get('lat')
    lon = request.form.get('lon')
    meden = request.form.get('meden')
    sahe = request.form.get('sahe')
    telefon = request.form.get('telefon')
    qeyd = request.form.get('qeyd')
    
    conn = get_db()
    try:
        conn.execute('''
            INSERT INTO quyular (quyu_no, lat, lon, meden, sahe, telefon, qeyd) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (quyu_no, float(lat), float(lon), meden, sahe, telefon, qeyd))
        conn.commit()
    except Exception as e:
        print("Xəta:", e)
    finally:
        conn.close()
    return redirect(url_for('admin'))

@app.route('/redakte/<int:id>', methods=['POST'])
def redakte(id):
    if not session.get('admin'):
        return redirect(url_for('login'))
    
    quyu_no = request.form.get('quyu_no')
    lat = request.form.get('lat')
    lon = request.form.get('lon')
    meden = request.form.get('meden')
    sahe = request.form.get('sahe')
    telefon = request.form.get('telefon')
    qeyd = request.form.get('qeyd')
    
    conn = get_db()
    conn.execute('''
        UPDATE quyular 
        SET quyu_no=?, lat=?, lon=?, meden=?, sahe=?, telefon=?, qeyd=?
        WHERE id=?
    ''', (quyu_no, float(lat), float(lon), meden, sahe, telefon, qeyd, id))
    conn.commit()
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

# Oflayn işləmək üçün Service Worker faylı
@app.route('/sw.js')
def sw():
    return app.send_static_file('sw.js')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
