import os
import json
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, static_folder='static')
app.secret_key = 'hendra-media-tech-secret-key-2026'

KATALOG_FILE = os.path.join(os.path.dirname(__file__), 'katalog.json')
KATEGORI_FILE = os.path.join(os.path.dirname(__file__), 'kategori.json')

# Kategori bawaan jika file belum ada
KATEGORI_DEFAULT = [
    {"id": "Pendidikan", "nama": "📚 Pendidikan & Literasi"},
    {"id": "Bisnis", "nama": "💼 Bisnis & Operasional UMKM"},
    {"id": "Acara", "nama": "🎉 Acara & Undangan Digital"},
    {"id": "Tools", "nama": "🛠️ Alat Bantu & Otomasi (Tools)"}
]

def load_json(filepath, default_value):
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return default_value
    return default_value

def save_json(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

ADMIN_USER = "admin"
ADMIN_PASS_HASH = generate_password_hash("hendra123")

# ==================================================
# ROUTE FILE LOGO / STATIC
# ==================================================
@app.route('/logo.jpg')
def serve_logo_jpg():
    return send_from_directory('static', 'logo.jpg')

@app.route('/logo.png')
def serve_logo_png():
    return send_from_directory('static', 'logo.png')

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

# ==================================================
# ROUTE UTAMA
# ==================================================
@app.route('/')
def home():
    kotaks = load_json(KATALOG_FILE, [])
    kategori_list = load_json(KATEGORI_FILE, KATEGORI_DEFAULT)
    return render_template('index.html', kotaks=kotaks, kategori_list=kategori_list, is_admin=session.get('is_admin'))

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
                <button type="submit" class="btn btn-warning w-100 fw-bold text-dark">Masuk</button>
            </form>
            <div class="text-center mt-3">
                <a href="/" class="text-muted small text-decoration-none">&larr; Kembali ke Beranda</a>
            </div>
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
        kategori = request.form.get('kategori', 'Bisnis').strip()
        penawaran = request.form.get('penawaran', '').strip()
        link_demo = request.form.get('link_demo', '').strip()
        link_pesan = request.form.get('link_pesan', '').strip()

        kotaks = load_json(KATALOG_FILE, [])
        
        new_item = {
            "id": len(kotaks) + 1,
            "judul": judul,
            "kategori": kategori,
            "penawaran": penawaran,
            "link_demo": link_demo,
            "link_pesan": link_pesan
        }
        
        kotaks.insert(0, new_item)
        save_json(KATALOG_FILE, kotaks)
        json_result = json.dumps(kotaks, indent=2, ensure_ascii=False)

    kategori_list = load_json(KATEGORI_FILE, KATEGORI_DEFAULT)
    return render_template('tambah.html', json_result=json_result, kategori_list=kategori_list)

# ==================================================
# ROUTE KELOLA KATEGORI (TAMBAH & HAPUS)
# ==================================================
@app.route('/admin/kategori/tambah', methods=['POST'])
def tambah_kategori():
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    
    nama = request.form.get('nama', '').strip()
    id_kat = request.form.get('id_kat', '').strip()
    
    if nama and id_kat:
        kategori_list = load_json(KATEGORI_FILE, KATEGORI_DEFAULT)
        # Cek agar ID tidak duplikat
        if not any(k['id'] == id_kat for k in kategori_list):
            kategori_list.append({"id": id_kat, "nama": nama})
            save_json(KATEGORI_FILE, kategori_list)
            flash('Kategori baru berhasil ditambahkan!', 'success')
        else:
            flash('ID Kategori sudah digunakan!', 'warning')
            
    return redirect(url_for('tambah_kotak'))

@app.route('/admin/kategori/hapus/<id_kat>', methods=['POST'])
def hapus_kategori(id_kat):
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    
    kategori_list = load_json(KATEGORI_FILE, KATEGORI_DEFAULT)
    kategori_list = [k for k in kategori_list if k['id'] != id_kat]
    save_json(KATEGORI_FILE, kategori_list)
    flash('Kategori berhasil dihapus!', 'info')
    
    return redirect(url_for('tambah_kotak'))

if __name__ == '__main__':
    app.run(debug=True)
