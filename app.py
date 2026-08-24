import sqlite3
import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify

app = Flask(__name__)
app.secret_key = 'azgerneft_secrety_key_123'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Admin şifrəniz (istəsəniz dəyişə bilərsiniz)
ADMIN_PASSWORD = "123" 

def init_db():
    conn = sqlite3.connect('neft_quyulari.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quyular (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quyu_no TEXT UNIQUE NOT NULL,
            meden TEXT,
            sahe TEXT,
            lokasiya TEXT,
            lat TEXT,
            lon TEXT,
            melumat TEXT,
            cavabdeh_ad TEXT,
            cavabdeh_tel TEXT,
            sekil TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    is_admin = session.get('is_admin', False)
    return render_template('index.html', is_admin=is_admin)

@app.route('/ara', methods=['GET'])
def ara():
    q = request.args.get('q', '').strip()
    conn = sqlite3.connect('neft_quyulari.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM quyular WHERE LOWER(quyu_no) LIKE LOWER(?)", ('%' + q + '%',))
    neticeler = cursor.fetchall()
    conn.close()
    return jsonify(neticeler)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            session['is_admin'] = True
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Xətalı şifrə!")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('is_admin', None)
    return redirect(url_for('index'))

@app.route('/elave-et', methods=['GET', 'POST'])
def elave_et():
    if not session.get('is_admin'):
        return "Bu səhifəyə yalnız Admin daxil ola bilər!", 403

    if request.method == 'POST':
        quyu_no = request.form['quyu_no']
        meden = request.form['meden']
        sahe = request.form['sahe']
        lokasiya = request.form['lokasiya']
        lat = request.form['lat']
        lon = request.form['lon']
        melumat = request.form['melumat']
        cavabdeh_ad = request.form['cavabdeh_ad']
        cavabdeh_tel = request.form['cavabdeh_tel']
        
        file = request.files.get('sekil')
        filename = ""
        if file and file.filename != '':
            filename = quyu_no + "_" + file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        conn = sqlite3.connect('neft_quyulari.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO quyular (quyu_no, meden, sahe, lokasiya, lat, lon, melumat, cavabdeh_ad, cavabdeh_tel, sekil)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (quyu_no, meden, sahe, lokasiya, lat, lon, melumat, cavabdeh_ad, cavabdeh_tel, filename))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
        
    return render_template('elave_et.html')

if __name__ == '__main__':
    if not os.path.exists('static/uploads'):
        os.makedirs('static/uploads')
    app.run(host='0.0.0.0', port=5000, debug=True)