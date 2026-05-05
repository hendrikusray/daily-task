# 🚀 Deployment Guide

Panduan lengkap untuk mendeploy aplikasi CMS ke berbagai platform gratis dan murah.

## 📋 Pre-deployment Checklist

- [ ] Change SECRET_KEY di `app.py` 
- [ ] Set `debug=False` di `app.py`
- [ ] Test aplikasi secara lokal
- [ ] Setup environment variables
- [ ] Database backup

## 🌐 Deployment Options

### 1️⃣ REPLIT (RECOMMENDED - PALING MUDAH)

**Keuntungan:**
- ✅ Gratis, no credit card needed
- ✅ Setup hanya 1 menit
- ✅ Unlimited projects
- ✅ Public URL instant

**Steps:**
1. Go to https://replit.com dan login/signup
2. Click "+ Create"
3. Pilih "Import from GitHub" atau upload files
4. Replit akan auto-detect Python project
5. Click "Run"
6. Copy public URL dan share!

**Bagian yang harus diubah di code:**
```python
# Di app.py, ubah line terakhir menjadi:
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=False, host='0.0.0.0', port=5000)
```

---

### 2️⃣ PYTHONANYWHERE (GRATIS TIER AVAILABLE)

**Keuntungan:**
- ✅ Gratis tier (pythonanywhere.com)
- ✅ Custom domain support
- ✅1 GB storage gratis

**Steps:**
1. Go to https://www.pythonanywhere.com
2. Sign up dengan akun baru
3. Di "Files" tab, upload project files
4. Go to "Web" tab → "Add a new web app"
5. Choose "Python 3.9" → "Flask"
6. Setup source code path: `/home/yourusername/mysite`
7. Go to WSGI file dan edit:

```python
# /var/www/yourusername_pythonanywhere_com_wsgi.py
import sys
path = '/home/yourusername/mysite'
if path not in sys.path:
    sys.path.append(path)

from app.app import app as application
```

8. Reload web app
9. Visit `yourusername.pythonanywhere.com`

---

### 3️⃣ RAILWAY.APP (GRATIS $5 CREDITS/BULAN)

**Keuntungan:**
- ✅ $5/bulan gratis credits
- ✅ Easy GitHub integration
- ✅ Auto-deploy on push
- ✅ Custom domain support

**Steps:**
1. Push project ke GitHub
2. Go to https://railway.app
3. Click "New Project"
4. Select "Deploy from GitHub"
5. Connect GitHub account dan select repo
6. Railway auto-detects Python & creates `Procfile`
7. Setup environment variables:
   - `FLASK_ENV=production`
   - `SECRET_KEY=your-secret-key`
8. Click "Deploy"
9. Get custom railway.app domain

**Konfigurasi Procfile:**
```
web: python app/app.py
```

---

### 4️⃣ HEROKU (NOW PAID, tapi Docker-friendly)

Heroku sekarang berbayar (~$7/month), tapi bisa pakai container. Alternative lebih baik: Railway atau Render.

---

### 5️⃣ RENDER.COM (GRATIS TIER)

**Keuntungan:**
- ✅ Gratis tier tersedia
- ✅ Auto-SSL
- ✅ GitHub integration

**Steps:**
1. Push ke GitHub
2. Go to https://render.com
3. Click "New +" → "Web Service"
4. Connect GitHub repo
5. Fill details:
   - Name: `my-cms`
   - Environment: `Python 3`
   - Build command: `pip install -r requirements.txt`
   - Start command: `python app/app.py`
6. Add environment variable:
   - `FLASK_ENV`: `production`
   - `SECRET_KEY`: `your-random-string`
7. Click "Create Web Service"

---

## 🔧 Pre-deployment Modifications

### 1. Update `app.py` untuk Production

```python
# Before deployment, change these lines:
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    # DEV:
    # app.run(debug=True, host='0.0.0.0', port=5000)
    
    # PRODUCTION:
    import os
    debug = os.getenv('FLASK_ENV') != 'production'
    app.run(debug=debug, host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
```

### 2. Update SECRET_KEY

```python
import os
from secrets import token_hex

# BEFORE (insecure):
app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'

# AFTER (secure):
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', token_hex(32))
```

### 3. Database untuk Production

SQLite OK untuk dev/testing kecil. Untuk production scalable, gunakan PostgreSQL:

```python
# Option: Upgrade ke PostgreSQL (masih gratis di banyak platform)
import os
database_url = os.getenv('DATABASE_URL', 'sqlite:///konten.db')
# Ganti sqlite dengan postgresql jika ada environment variable
```

---

## 📦 Create Production Configs

### File: `deployment/.env.example`
```
FLASK_ENV=production
SECRET_KEY=your-random-secret-key-here-min-32-chars
DATABASE_URL=sqlite:///konten.db
PORT=5000
```

### File: `deployment/wsgi.py`
```python
import os
import sys

# Add your project to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app.app import app

if __name__ == "__main__":
    app.run()
```

### File: `deployment/Procfile` (untuk Heroku/Railway)
```
web: gunicorn app.app:app --log-file -
```

Install gunicorn untuk production:
```bash
pip install gunicorn
pip freeze > requirements.txt
```

---

## 🔐 Security Checklist

Sebelum deploy:

- [ ] Change SECRET_KEY ke random string yang aman
- [ ] Set `debug=False` untuk production
- [ ] Setup environment variables (jangan hardcode passwords)
- [ ] Enable HTTPS (auto pada kebanyakan platform)
- [ ] Set CORS headers jika ada API
- [ ] Regular backup database
- [ ] Monitor error logs
- [ ] Update dependencies regular

---

## 🚀 Quick Deploy Recipes

### Railway.app (Fastest)
```bash
# 1. Push to GitHub
git add .
git commit -m "Ready to deploy"
git push

# 2. Go to railway.app, connect GitHub, done!
```

### PythonAnywhere (Most Stable)
```bash
# 1. Upload files via web
# 2. Edit WSGI file
# 3. Reload
# Done!
```

### Replit (Easiest)
```bash
# 1. Go to replit.com
# 2. Import GitHub repo
# 3. Click Run
# 4. Share public URL
```

---

## 📊 Expected Costs

| Platform | Cost | Notes |
|----------|------|-------|
| Replit | FREE | Unlimited for free tier |
| PythonAnywhere | FREE/PAID | $5/mo for custom domain |
| Railway | PAID | $5/mo free credits |
| Render | FREE/PAID | Free tier available |
| Heroku | PAID | $7/mo minimum |

**Recommendation:** Start dengan **Replit** (gratis), upgrade ke **Railway** atau **PythonAnywhere** saat ready untuk production.

---

## 🔄 Continuous Deployment

Untuk auto-deploy saat update GitHub:

**Railway** (Best):
- Automatic on GitHub push
- Set webhook otomatis

**Render**:
- Automatic on GitHub push
- Zero config

**PythonAnywhere**:
- Manual atau setup webhook

---

## 📈 Scaling (Jika Traffic Naik)

1. **Database**: Upgrade dari SQLite → PostgreSQL (Railway: $7-20/mo)
2. **Storage**: Tambah file uploads (S3 atau Firebase)
3. **CDN**: Tambah Cloudflare untuk caching (FREE tier)
4. **Monitoring**: Setup error tracking (Sentry: FREE tier)

---

## ❓ Troubleshooting

**503 Service Unavailable**
- Check logs di dashboard platform
- Verify environment variables
- Restart application

**Database Locked**
- SQLite issue jika concurrent users tinggi
- Upgrade ke PostgreSQL

**Static Files Not Loading**
- Jalankan `python app.py` di folder yang benar
- Check CSS path di templates

---

## 📞 Support

Platform support links:
- Replit: https://replit.com/support
- Railway: https://docs.railway.app
- Render: https://render.com/docs
- PythonAnywhere: https://www.pythonanywhere.com/help/

---

**Happy Deploying! 🎉**
