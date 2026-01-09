import requests
import json

# --- ISI API KEY KAMU DI SINI ---
MY_API_KEY = "IAIzaSyCBIYir4MWyExZxmcsc3ruGQfXKkSjn-7M"

print("Sedang menghubungi Google...")

url = f"https://generativelanguage.googleapis.com/v1beta/models?key={MY_API_KEY}"
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    print("\n✅ DAFTAR MODEL YANG BISA KAMU PAKAI:")
    for model in data.get('models', []):
        # Kita cari model yang bisa generateContent (bisa baca gambar/chat)
        if "generateContent" in model.get("supportedGenerationMethods", []):
            name = model['name'].replace("models/", "")
            print(f"- {name}")
    print("\nCATAT salah satu nama di atas (misal: gemini-1.5-flash-latest)")
else:
    print(f"❌ Error API Key: {response.text}")