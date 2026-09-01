import os
import json
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'hendra-media-tech-secret-key-2026'

# Path file penyimpanan data JSON
KATALOG_FILE = os.path.join(os.path.dirname(__file__), 'katalog.json')

def load_katalog():
    if os.path.exists(KATALOG_FILE):
        try:
            with open(KATALOG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_katalog(data):
    with open(KATALOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Akun Admin Sederhana
ADMIN_USER = "admin"
ADMIN_PASS_HASH = generate_password_hash("hendra123")

@app.route('/')
def home():
    kotaks = load_katalog()
    return render_template('index.html', kotaks=kotaks)

@app.route('/admin/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == ADMIN_USER and check_password_hash(ADMIN_PASS_HASH, password):
            session['is_admin'] = True
            return redirect(url_for('tambah_kotak'))
        else:
            flash('Username atau Password salah!', 'danger')
    return '''
    <!DOCTYPE html>
    <html lang="id">
    <head>
        <meta charset="UTF-8">
        <title>Login Admin - Hendra Media Tech</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body style="background:#0b132b; color:#fff; display:flex; align-items:center; justify-content:center; min-height:100vh;">
        <div class="card p-4 bg-dark text-white border-warning" style="max-width:380px; width:100%;">
            <h4 class="text-warning text-center fw-bold mb-3">🔑 Login Admin</h4>
            <form method="POST">
                <input type="text" name="username" class="form-control mb-3 bg-secondary text-white" placeholder="Username" required>
                <input type="password" name="password" class="form-control mb-3 bg-secondary text-white" placeholder="Password" required>
                <button type="submit" class="btn btn-warning w-100 fw-bold">Masuk</button>
            </form>
        </div>
    </body>
    </html>
    '''

@app.route('/admin/logout')
def logout():
    session.pop('is_admin', None)
    return redirect(url_for('home'))

@app.route('/admin/tambah', methods=['GET', 'POST'])
def tambah_kotak():
    if not session.get('is_admin'):
        return redirect(url_for('login'))

    json_result = None
    if request.method == 'POST':
        judul = request.form.get('judul', '').strip()
        penawaran = request.form.get('penawaran', '').strip()
        link_demo = request.form.get('link_demo', '').strip()
        link_pesan = request.form.get('link_pesan', '').strip()

        kotaks = load_katalog()
        
        new_item = {
            "id": len(kotaks) + 1,
            "judul": judul,
            "penawaran": penawaran,
            "link_demo": link_demo,
            "link_pesan": link_pesan
        }
        
        kotaks.insert(0, new_item)
        save_katalog(kotaks)
        json_result = json.dumps(kotaks, indent=2, ensure_ascii=False)

    return render_template('tambah.html', json_result=json_result)

if __name__ == '__main__':
    app.run(debug=True)
