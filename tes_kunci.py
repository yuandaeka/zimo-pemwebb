import requests
import json

# --- MASUKKAN API KEY YANG SUDAH BENAR TADI ---
MY_API_KEY = "AIzaSyCBIYir4MWyExZxmcsc3ruGQfXKkSjn-7M"

print("Sedang meminta daftar model ke Google...")

# Kita pakai metode GET untuk minta daftar, bukan POST untuk chat
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={MY_API_KEY}"
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    print("\n✅ DAFTAR MODEL YANG TERSEDIA:")
    
    # Filter hanya model yang bisa generateContent (Chat/Vision)
    model_ketemu = False
    for m in data.get('models', []):
        if "generateContent" in m.get("supportedGenerationMethods", []):
            # Kita buang awalan 'models/' biar bersih
            nama_bersih = m['name'].replace("models/", "")
            print(f"- {nama_bersih}")
            model_ketemu = True
            
    if not model_ketemu:
        print("⚠️ Tidak ada model chat yang aktif. Cek Project Google Cloud kamu.")
    else:
        print("\n👉 PILIH SALAH SATU NAMA DI ATAS UNTUK DIPASANG DI APP.PY")
        
else:
    print(f"❌ Masih Gagal Connect: {response.text}")