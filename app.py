import os
import json
import io
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory, send_file
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, static_folder='static')
app.secret_key = 'hendra-media-tech-secret-key-2026'

KATALOG_FILE = '/tmp/katalog.json'
KATEGORI_FILE = '/tmp/kategori.json'

KATEGORI_DEFAULT = [
    {"id": "Pendidikan", "nama": "📚 Pendidikan & Literasi"},
    {"id": "Bisnis", "nama": "💼 Bisnis & Operasional UMKM"},
    {"id": "Acara", "nama": "🎉 Acara & Undangan Digital"},
    {"id": "Tools", "nama": "🛠️ Alat Bantu & Otomasi (Tools)"}
]

# Ditetapkan presisi sesuai request
KATALOG_DEFAULT = [
    {
        "id": 1,
        "judul": "Sistem Kasir (POS) & Manajer Stok Toko",
        "kategori": "Bisnis",
        "penawaran": "Pencatatan transaksi penjualan harian, cetak struk via Bluetooth, analisis keuntungan, dan pengingat stok menipis untuk warung/toko kelontong/kafe.",
        "link_demo": "https://demo-pos-kasir-ten.vercel.app/",
        "link_pesan": "https://wa.me/6282122900593"
    },
    {
        "id": 2,
        "judul": "Web Restoran / Cafe dengan Menu QR Code",
        "kategori": "Bisnis",
        "penawaran": "Pelanggan tinggal scan QR code di meja untuk lihat menu, pilih makanan, dan kirim pesanan otomatis ke WhatsApp kasir/dapur.",
        "link_demo": "https://demo-menu-qr-resto.vercel.app/",
        "link_pesan": "https://wa.me/6282122900593"
    },
    {
        "id": 3,
        "judul": "Web Pencatatan Utang & Keuangan Harian",
        "kategori": "Bisnis",
        "penawaran": "Pencatatan arus kas masuk/keluar harian, piutang pelanggan, serta fitur generate rekap laporan keuangan bulanan format PDF.",
        "link_demo": "https://demo-buku-kas-hendra.vercel.app/",
        "link_pesan": "https://wa.me/6282122900593"
    }
]

def load_json(filepath, default_value):
    if not os.path.exists(filepath):
        save_json(filepath, default_value)
        return default_value
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Jika file kosong atau datanya lebih sedikit dari default bawaan, paksakan perbarui file /tmp/
            if not data or (isinstance(data, list) and len(data) < len(default_value)):
                save_json(filepath, default_value)
                return default_value
            return data
    except Exception:
        save_json(filepath, default_value)
        return default_value

def save_json(filepath, data):
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

ADMIN_USER = "admin"
ADMIN_PASS_HASH = generate_password_hash("hendra123")

@app.route('/logo.jpg')
def serve_logo_jpg():
    return send_from_directory('static', 'logo.jpg')

@app.route('/logo.png')
def serve_logo_png():
    return send_from_directory('static', 'logo.png')

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.route('/')
def home():
    kotaks = load_json(KATALOG_FILE, KATALOG_DEFAULT)
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

        kotaks = load_json(KATALOG_FILE, KATALOG_DEFAULT)
        new_id = max([k.get('id', 0) for k in kotaks], default=0) + 1
        
        new_item = {
            "id": new_id,
            "judul": judul,
            "kategori": kategori,
            "penawaran": penawaran,
            "link_demo": link_demo,
            "link_pesan": link_pesan
        }
        
        kotaks.insert(0, new_item)
        save_json(KATALOG_FILE, kotaks)
        json_result = json.dumps(kotaks, indent=2, ensure_ascii=False)
        flash('Kotak layanan berhasil ditambahkan!', 'success')

    kotaks_list = load_json(KATALOG_FILE, KATALOG_DEFAULT)
    kategori_list = load_json(KATEGORI_FILE, KATEGORI_DEFAULT)
    return render_template('tambah.html', json_result=json_result, kategori_list=kategori_list, kotaks_list=kotaks_list)

@app.route('/admin/kotak/hapus/<int:kotak_id>', methods=['POST'])
def hapus_kotak(kotak_id):
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    
    kotaks = load_json(KATALOG_FILE, KATALOG_DEFAULT)
    kotaks = [k for k in kotaks if k.get('id') != kotak_id]
    save_json(KATALOG_FILE, kotaks)
    
    flash('Kotak layanan berhasil dihapus!', 'info')
    return redirect(url_for('tambah_kotak'))

@app.route('/admin/kategori/tambah', methods=['POST'])
def tambah_kategori():
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    
    nama = request.form.get('nama', '').strip()
    id_kat = request.form.get('id_kat', '').strip()
    
    if nama and id_kat:
        kategori_list = load_json(KATEGORI_FILE, KATEGORI_DEFAULT)
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

@app.route('/admin/backup/<pilihan>')
def backup_data(pilihan):
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    
    if pilihan == 'katalog':
        filename = KATALOG_FILE
        download_name = 'backup_katalog_hendra.json'
    elif pilihan == 'kategori':
        filename = KATEGORI_FILE
        download_name = 'backup_kategori_hendra.json'
    else:
        return redirect(url_for('tambah_kotak'))

    if os.path.exists(filename):
        return send_file(filename, as_attachment=True, download_name=download_name, mimetype='application/json')
    else:
        flash('File data tidak ditemukan untuk dibackup.', 'danger')
        return redirect(url_for('tambah_kotak'))

@app.route('/admin/restore/<pilihan>', methods=['POST'])
def restore_data(pilihan):
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    
    if 'file_json' not in request.files:
        flash('Tidak ada file yang diunggah.', 'warning')
        return redirect(url_for('tambah_kotak'))
    
    file = request.files['file_json']
    if file.filename == '':
        flash('Nama file kosong.', 'warning')
        return redirect(url_for('tambah_kotak'))

    if pilihan == 'katalog':
        target_file = KATALOG_FILE
    elif pilihan == 'kategori':
        target_file = KATEGORI_FILE
    else:
        return redirect(url_for('tambah_kotak'))

    if file and file.filename.endswith('.json'):
        try:
            stream = io.BytesIO(file.read())
            data = json.load(stream)
            save_json(target_file, data)
            flash(f'Data {pilihan} berhasil direstore!', 'success')
        except json.JSONDecodeError:
            flash('Gagal restore. File bukan format JSON yang valid.', 'danger')
        except Exception as e:
            flash(f'Terjadi kesalahan: {str(e)}', 'danger')
    else:
        flash('Hanya diperbolehkan mengunggah file .json.', 'danger')

    return redirect(url_for('tambah_kotak'))

if __name__ == '__main__':
    app.run(debug=True)
