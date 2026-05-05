# ✅ SETUP CHECKLIST & VERIFICATION

Gunakan checklist ini untuk memastikan semuanya berjalan dengan baik.

## 🔍 Pre-Setup Verification

- [ ] Python 3.8+ installed: `python3 --version`
- [ ] Project folder created: `/Users/Hendri/Documents/ray/daily-task`
- [ ] All files present (check list below)
- [ ] README.md readable
- [ ] requirements.txt has all packages

## 📁 File Verification

### Core Files
- [ ] `app/app.py` (Main application - 500+ lines)
- [ ] `app/templates/base.html` (Base template)
- [ ] `app/templates/login.html` (Login page)
- [ ] `app/templates/register.html` (Register page)
- [ ] `app/templates/dashboard.html` (Dashboard)
- [ ] `app/templates/buat_konten.html` (Create content)
- [ ] `app/templates/edit_konten.html` (Edit content)
- [ ] `app/templates/profile.html` (Profile page)
- [ ] `app/static/css/style.css` (Styling - 600+ lines)

### Config Files
- [ ] `requirements.txt` (Dependencies)
- [ ] `README.md` (Main documentation)
- [ ] `QUICKSTART.md` (Quick start guide)
- [ ] `PROJECT_SUMMARY.md` (Project overview)
- [ ] `.gitignore` (Git ignore rules)

### Deployment Files
- [ ] `deployment/DEPLOYMENT.md` (Deployment guide)
- [ ] `deployment/.env.example` (Environment template)
- [ ] `deployment/Procfile` (Heroku/Railway config)
- [ ] `deployment/wsgi.py` (WSGI server)

### Launcher Scripts
- [ ] `run.sh` (Mac/Linux launcher)
- [ ] `run.bat` (Windows launcher)

### Optional Docker
- [ ] `Dockerfile` (Docker container config)
- [ ] `docker-compose.yml` (Docker Compose config)

## 🚀 Installation Steps

### Step 1: Navigate to Project
```bash
cd /Users/Hendri/Documents/ray/daily-task
```
- [ ] Confirm you're in correct folder
- [ ] List files: `ls -la`

### Step 2: Create Virtual Environment
```bash
python3 -m venv venv
```
- [ ] Folder `venv/` created
- [ ] No errors shown

### Step 3: Activate Virtual Environment

**Mac/Linux:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate.bat
```

- [ ] Prompt shows `(venv)` prefix
- [ ] No errors

### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

- [ ] Flask installed ✓
- [ ] Flask-SQLAlchemy installed ✓
- [ ] Flask-Login installed ✓
- [ ] Werkzeug installed ✓
- [ ] No errors

### Step 5: Run Application

**Using Script (Recommended):**
```bash
# Mac/Linux
chmod +x run.sh
./run.sh

# Windows
run.bat
```

**Manual:**
```bash
cd app
python app.py
```

- [ ] Output shows "Running on http://127.0.0.1:5000"
- [ ] No error messages
- [ ] Server is running

## 🌐 Testing Application

### Browser Test
- [ ] Open: http://localhost:5000
- [ ] Redirected to login page
- [ ] URL shows `/login`

### Login Test (Should FAIL - No Account Yet)
- [ ] Click login page loads
- [ ] Form has "Username" field
- [ ] Form has "Password" field
- [ ] Has "Daftar di sini" link

### Register Test (NEW ACCOUNT)
- [ ] Click "Daftar di sini"
- [ ] Register form loads
- [ ] Fill: username, email, password, confirm password
- [ ] Click "Daftar"
- [ ] Success message shown
- [ ] Redirected to login page

### Login Test (With Account)
- [ ] Enter username you just created
- [ ] Enter password
- [ ] Click "Login"
- [ ] Success message shown
- [ ] Dashboard loads
- [ ] Shows "Total Konten: 0"

### Create Content Test
- [ ] Click "+ Buat Konten Baru"
- [ ] Form loads with 3 fields
- [ ] Fill judul, deskripsi, isi
- [ ] Click "Simpan Konten"
- [ ] Success message shown
- [ ] Back on dashboard
- [ ] Content appears as card
- [ ] Shows creation time

### Edit Content Test
- [ ] Click "Edit" button on content
- [ ] Form loads with existing data
- [ ] Modify content
- [ ] Click "Simpan Perubahan"
- [ ] Success message shown
- [ ] Changes visible on dashboard

### Delete Content Test
- [ ] Click "Hapus" button
- [ ] Confirmation dialog appears
- [ ] Confirm deletion
- [ ] Content removed from dashboard
- [ ] Success message shown

### Profile Test
- [ ] Click "Profil" in navbar
- [ ] Profile page loads
- [ ] Shows username
- [ ] Shows email
- [ ] Shows "Member Sejak" date
- [ ] Shows total content count

### Logout Test
- [ ] Click "Logout" in navbar
- [ ] Logged out message shown
- [ ] Redirected to login page
- [ ] Cannot access dashboard

### Create Second Account Test
- [ ] Repeat register with different account
- [ ] Login with account 1
- [ ] Create content with account 1
- [ ] Logout
- [ ] Login with account 2
- [ ] Verify account 2 cannot see account 1's content
- [ ] Dashboard empty for account 2

## 🐛 Troubleshooting

If any test fails:

### Error: `ModuleNotFoundError: No module named 'flask'`
```bash
# Make sure venv is activated (should see (venv) in prompt)
source venv/bin/activate
pip install -r requirements.txt
```

### Error: `Address already in use` port 5000
Edit `app/app.py` last line, change `port=5000` to `port=8000`:
```python
app.run(debug=True, host='0.0.0.0', port=8000)
```

### Error: Database locked
Delete `app/konten.db` and restart:
```bash
rm app/konten.db
python app/app.py
```

### Error: Template not found
Check that `templates/` folder has all 7 HTML files in correct location

### Static files (CSS) not loading
Check browser console for 404 errors
Verify `static/css/style.css` exists
Restart Flask app

### Application won't start
Check port 5000 not in use: `lsof -i :5000`
Verify Python 3.8+ installed: `python3 --version`
Check all requirements installed: `pip list`

## 📊 Final Verification

After all tests pass:

- [ ] Application runs without errors
- [ ] Login/Register works
- [ ] CRUD operations work
- [ ] Multiple users can login separately
- [ ] Each user sees only own content
- [ ] UI looks good and responsive
- [ ] No console errors in terminal
- [ ] No 404 errors in browser

## 🎉 Success Criteria

If ALL checkboxes are checked:
✅ **Application is ready to use!**

## 🚀 Next: Deployment

Once fully tested locally:
1. Read `deployment/DEPLOYMENT.md`
2. Choose deployment platform (Replit, Railway, etc.)
3. Follow deployment guide
4. Test on production
5. Share URL with users!

---

**All checks passed? Great! You're ready to go! 🚀**
