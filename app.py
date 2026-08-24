from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = 'azgerneft_secret_key_change_in_production'

# SQLite verilənlər bazası konfiqurasiyası
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///wells.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- Verilənlər Bazası Modelləri ---

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Well(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    coordinate = db.Column(db.String(100), nullable=False)
    lat = db.Column(db.Float, nullable=False)
    lng = db.Column(db.Float, nullable=False)

# Admin tələb edən routelar üçün dekorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Admin panelə daxil olmaq üçün giriş edin.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- Routelar ---

@app.route('/')
def index():
    search_query = request.args.get('search', '').strip()
    if search_query:
        # Quyu adı və ya nömrəsinə görə axtarış
        wells = Well.query.filter(
            (Well.name.ilike(f'%{search_query}%')) | 
            (Well.number.cast(db.String).ilike(f'%{search_query}%'))
        ).all()
    else:
        wells = Well.query.all()
    
    return render_template('index.html', wells=wells, search=search_query)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        # Parolun doğru olub-olmaması yoxlanılır
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Uğurla daxil oldunuz!', 'success')
            return redirect(url_for('admin'))
        else:
            flash('İstifadəçi adı və ya parol yanlışdır!', 'danger')

    return '''
    <!DOCTYPE html>
    <html lang="az">
    <head>
        <meta charset="UTF-8">
        <title>Admin Giriş</title>
        <style>
            body { background: #0b1524; color: #fff; font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
            .login-card { background: #202d3d; padding: 30px; border-radius: 8px; width: 320px; box-shadow: 0 4px 10px rgba(0,0,0,0.3); }
            input { width: 100%; padding: 10px; margin: 10px 0; border-radius: 4px; border: 1px solid #dfc27c; background: #111d2d; color: #fff; box-sizing: border-box; }
            button { width: 100%; padding: 10px; background: #dfc27c; border: none; font-weight: bold; cursor: pointer; border-radius: 4px; color: #0b1524; }
            .alert { color: #ff6b6b; font-size: 14px; margin-bottom: 10px; }
        </style>
    </head>
    <body>
        <div class="login-card">
            <h2>Admin Giriş</h2>
            <form method="POST">
                <input type="text" name="username" placeholder="İstifadəçi adı" required>
                <input type="password" name="password" placeholder="Parol" required>
                <button type="submit">Daxil ol</button>
            </form>
        </div>
    </body>
    </html>
    '''

@app.route('/admin')
@login_required
def admin():
    wells = Well.query.all()
    return f'''
    <h1>Admin Panel</h1>
    <p>Xoş gəldiniz, {session.get('username')}! | <a href="/logout">Çıxış</a> | <a href="/">Əsas Səhifə</a></p>
    <hr>
    <h3>Quyuların Siyahısı</h3>
    <ul>
        {"".join([f"<li>{w.name} ({w.coordinate})</li>" for w in wells])}
    </ul>
    '''

@app.route('/logout')
def logout():
    session.clear()
    flash('Çıxış edildi.', 'info')
    return redirect(url_for('login'))

# Verilənlər bazasını yaradan və ilkin admin istifadəçisini əlavə edən hissə
def init_db():
    with app.app_context():
        db.create_all()
        # Əgər admin yoxdursa yaradılır
        if not User.query.filter_by(username='admin').first():
            default_admin = User(username='admin')
            default_admin.set_password('admin123')  # Susmaya görə parol
            db.session.add(default_admin)
            
            # Test üçün nümunə quyu
            if not Well.query.first():
                sample_well = Well(
                    number=1,
                    name="Quyu №102",
                    coordinate="40.3772, 49.8920",
                    lat=40.3772,
                    lng=49.8920
                )
                db.session.add(sample_well)
            
            db.session.commit()

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
