# 🚀 QUICK START

## 1. Install Dependencies (Run once)
```bash
cd /Users/Hendri/Documents/ray/daily-task
pip install -r requirements.txt
```

## 2. Run Application
```bash
cd app
python app.py
```

## 3. Open Browser
Open: **http://localhost:5000**

## 4. Create Account
- Click "Daftar di sini" (Register)
- Fill username, email, password
- Click "Daftar"

## 5. Login
- Enter username & password
- Click "Login"

## 6. Create Content
- Click "+ Buat Konten Baru"
- Fill judul, deskripsi, isi konten
- Click "Simpan Konten"

## 7. Manage Content
- Edit: Click "Edit" button
- Delete: Click "Hapus" button
- View Profile: Click "Profil" di navbar

---

## 📁 Project Structure

```
daily-task/
├── README.md                 ← Dokumentasi lengkap
├── requirements.txt          ← Python packages
├── .gitignore               ← Git ignore list
├── QUICKSTART.md            ← File ini
├── app/
│   ├── app.py               ← Main application
│   ├── templates/           ← HTML files
│   ├── static/css/          ← CSS styling
│   └── konten.db            ← Database (auto-generated)
└── deployment/              ← Deployment configs
    ├── DEPLOYMENT.md        ← How to deploy
    ├── .env.example         ← Environment template
    ├── Procfile             ← For Railway/Heroku
    └── wsgi.py              ← For production server
```

---

## 🎯 Test Account (Development)

You can create multiple accounts and test with each:
1. Test Account 1: username: `user1` / password: `pass123`
2. Test Account 2: username: `user2` / password: `pass456`

Each user has separate content - cannot see others' content.

---

## 🛑 Stop Application

Press `Ctrl + C` in terminal to stop the server.

---

## 🔧 Useful Commands

### Restart with Fresh Database
```bash
rm app/konten.db
python app.py
```

### Use Different Port (if 5000 is busy)
Edit `app.py` last line, change `port=5000` to `port=8000`:
```python
app.run(debug=True, host='0.0.0.0', port=8000)
```

### Install Additional Packages
```bash
pip install package-name
pip freeze > requirements.txt  # Update requirements
```

---

## 📚 Next Steps

1. **Explore the Code**: Read `app.py` to understand how it works
2. **Customize**: Change colors in `app/static/css/style.css`
3. **Deploy**: Follow `deployment/DEPLOYMENT.md` for free deployment
4. **Add Features**: Implement categories, tags, search, etc.

---

## ❓ Help

- **Database issues?** Delete `konten.db` and restart
- **Port already in use?** Change port in `app.py`
- **ModuleNotFoundError?** Run `pip install -r requirements.txt`
- **Deployment help?** Read `deployment/DEPLOYMENT.md`

---

**Enjoy your CMS! 🎉**
