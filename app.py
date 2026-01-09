import sqlite3
from flask import Flask, render_template, request
import requests
import base64
import json
import re  # <--- WAJIB ADA: Untuk mencari teks spesifik dari jawaban AI

app = Flask(__name__)

# ==========================================
# KONFIGURASI PENTING
# ==========================================
# 1. Masukkan API Key kamu
API_KEY = "AIzaSyBi-JgKCprHyKTA4PBtLECZwvLooJPCXbk"

# 2. NAMA MODEL
MODEL_NAME = "gemini-flash-latest" 
# ==========================================

# ==========================================
# FUNGSI DATABASE
# ==========================================
def init_db():
    conn = sqlite3.connect('zimo.db')
    c = conn.cursor()
    # Kita buat tabel history jika belum ada
    c.execute('''CREATE TABLE IF NOT EXISTS history
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  makanan TEXT, 
                  kalori TEXT, 
                  tanggal TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

# Panggil fungsi ini sekali saat aplikasi dijalankan
init_db()


# ==========================================
# ROUTING APLIKASI
# ==========================================
@app.route('/', methods=['GET', 'POST'])
def home():
    hasil_analisis = None
    pesan_error = None

    if request.method == 'POST':
        # 1. Ambil File Foto
        files = request.files.getlist('file_foto')
        file_pilihan = None
        
        # Cari file yang tidak kosong
        for f in files:
            if f.filename != '':
                file_pilihan = f
                break
        
        if not file_pilihan:
            pesan_error = "Kamu belum memilih foto."
        else:
            try:
                print(f"--- Memproses Foto: {file_pilihan.filename} ---")
                
                # 2. Ubah Gambar ke Base64
                image_data = file_pilihan.read()
                base64_image = base64.b64encode(image_data).decode('utf-8')

                # 3. Kirim ke Google Gemini
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={API_KEY}"
                headers = {'Content-Type': 'application/json'}
                
                # 4. PROMPT (Instruksi)
                instruksi_ai = """
                You are Zimo, a personal nutrition assistant. Your task is:
                1. Identify the food in this photo in detail.
                2. Estimate its weight (in grams).
                3. Breakdown the composition and calories.
                4. Provide total calories.

                Answer ONLY using the following HTML format (strict):
                
                <h3>🍽️ Zimo Analysis Result</h3>
                <p><b>Food:</b> [Food Name]</p>
                <hr style="margin: 10px 0; border: 0; border-top: 1px dashed #ccc;">
                <p><b>Composition Details:</b></p>
                <ul style="padding-left: 20px; margin-top: 5px;">
                    <li>[Ingredient 1]: <b>±[Number] g</b></li>
                    <li>[Ingredient 2]: <b>±[Number] g</b></li>
                </ul>
                <p><b>Estimated Weight:</b> ±[Number] gram</p>
                <p><b>Total Calories:</b> <span style='color:red; font-weight:bold;'>[Number] kcal</span></p>
                <hr>
                <p><b>Zimo's Comment:</b> [Short advice]</p>
                """

                payload = {
                    "contents": [{
                        "parts": [
                            {"text": instruksi_ai},
                            {"inline_data": {
                                "mime_type": "image/jpeg",
                                "data": base64_image
                            }}
                        ]
                    }]
                }

                print(f"--- Mengirim ke Model: {MODEL_NAME}... ---")
                response = requests.post(url, headers=headers, json=payload)
                
                # 5. Cek Jawaban
                if response.status_code == 200:
                    data = response.json()
                    hasil_analisis = data['candidates'][0]['content']['parts'][0]['text']
                    print("--- SUKSES! Dapat Jawaban ---")

                    # ====================================================
                    # BAGIAN BARU: EKSTRAK DATA & SIMPAN KE DATABASE
                    # ====================================================
                    try:
                        # Kita gunakan 're' (Regex) untuk mencari teks di dalam tag HTML
                        
                        # 1. Cari teks setelah <b>Food:</b>
                        cari_makanan = re.search(r"<b>Food:</b>\s*(.*?)</p>", hasil_analisis, re.IGNORECASE)
                        nama_makanan = cari_makanan.group(1) if cari_makanan else "Unknown Food"

                        # 2. Cari teks di dalam tag <span> (Total Calories)
                        cari_kalori = re.search(r"<b>Total Calories:</b>.*?>(.*?)</span>", hasil_analisis, re.IGNORECASE)
                        jumlah_kalori = cari_kalori.group(1) if cari_kalori else "0 kcal"

                        print(f"Menyimpan ke DB -> Makanan: {nama_makanan}, Kalori: {jumlah_kalori}")

                        # 3. Masukkan ke SQLite
                        conn = sqlite3.connect('zimo.db')
                        c = conn.cursor()
                        c.execute("INSERT INTO history (makanan, kalori) VALUES (?, ?)", (nama_makanan, jumlah_kalori))
                        conn.commit()
                        conn.close()
                        print("✅ Berhasil tersimpan di Database!")

                    except Exception as e_db:
                        print(f"⚠️ Gagal simpan ke DB (tapi hasil tetap muncul): {e_db}")
                    # ====================================================

                else:
                    error_msg = response.json().get('error', {}).get('message', 'Unknown Error')
                    pesan_error = f"Google Menolak: {error_msg}"
                    print(pesan_error)

            except Exception as e:
                pesan_error = f"Error Sistem: {str(e)}"
                print(pesan_error)

    return render_template('scan.html', hasil=hasil_analisis, error=pesan_error)

# Rute tambahan untuk melihat isi database (Bonus)
@app.route('/history')
def history_page():
    conn = sqlite3.connect('zimo.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM history ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    
    # Tampilkan JSON sederhana dulu untuk ngecek
    hasil_list = []
    for r in rows:
        hasil_list.append(f"{r['tanggal']} - {r['makanan']} ({r['kalori']})")
    
    return "<br>".join(hasil_list)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)