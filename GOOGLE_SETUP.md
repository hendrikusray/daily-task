# Setup Google Login & Google Drive Upload

## 1. Buat Google Cloud Project

1. Buka [console.cloud.google.com](https://console.cloud.google.com)
2. Klik **"New Project"** → beri nama (contoh: `marianne-tracker`) → **Create**

## 2. Enable API yang diperlukan

Dari menu kiri: **APIs & Services → Library**, cari dan enable:
- **Google Drive API**
- **Google People API** (opsional, untuk nama profil)

## 3. Buat OAuth 2.0 Credentials

1. **APIs & Services → Credentials → Create Credentials → OAuth client ID**
2. Pilih **Application type: Web application**
3. Beri nama: `Marianne Tracker`
4. Di bagian **Authorized redirect URIs**, tambahkan:
   - `http://localhost:5000/auth/google/callback` (untuk lokal/development)
   - `https://yourdomain.com/auth/google/callback` (untuk production — ganti domain)
5. Klik **Create** → copy **Client ID** dan **Client Secret**

## 4. OAuth Consent Screen

1. **APIs & Services → OAuth consent screen**
2. Pilih **External** → Fill:
   - App name: `Marianne Tracker`
   - User support email: email kamu
   - Developer contact email: email kamu
3. **Scopes**: tambahkan `../auth/userinfo.email`, `../auth/userinfo.profile`, `../auth/drive.file`
4. **Test users**: tambahkan email yang akan dipakai login (selama status Testing)

## 5. Set Environment Variables

Sebelum menjalankan app, set variabel ini di terminal:

```bash
export GOOGLE_CLIENT_ID="your-client-id-here.apps.googleusercontent.com"
export GOOGLE_CLIENT_SECRET="your-client-secret-here"
```

Atau buat file `.env` dan load dengan python-dotenv, atau set di Dockerfile/server config.

## 6. Jalankan App

```bash
source venv/bin/activate
python3 app/app.py
```

Sekarang di halaman login akan muncul tombol **"Login dengan Google"**. Setelah login dengan Google, tombol **"Upload ke Drive"** juga aktif di form tambah/edit campaign.

## Catatan

- **`drive.file` scope**: App hanya bisa akses file yang dia sendiri upload. File konten user lainnya di Drive tetap aman.
- File yang diupload akan otomatis diberi akses **"Anyone with the link can view"** agar link bisa dibuka tanpa login Google.
- Jika belum set `GOOGLE_CLIENT_ID`, tombol Google login tidak akan muncul (fitur non-aktif secara graceful).
