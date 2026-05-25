import os
import re
import uuid
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date, datetime, timedelta
from sqlalchemy import inspect, or_, text

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')

_db_url = os.environ.get('DATABASE_URL', 'sqlite:///konten.db')
if _db_url.startswith('postgres://'):
    _db_url = _db_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = _db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 280,
}

# ---- Google OAuth / Drive ----
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', '')
_CREDS_FILE = os.path.join(os.path.dirname(__file__), 'google_credentials.json')
if not GOOGLE_CLIENT_ID and os.path.exists(_CREDS_FILE):
    import json as _json
    with open(_CREDS_FILE) as _f:
        _creds_data = _json.load(_f).get('web', {})
    GOOGLE_CLIENT_ID = _creds_data.get('client_id', '')
    GOOGLE_CLIENT_SECRET = _creds_data.get('client_secret', '')

GOOGLE_SCOPES = [
    'openid',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/drive.file',
]
# Allow OAuth over HTTP in local dev (set PRODUCTION=1 in env to disable)
if not os.environ.get('PRODUCTION'):
    os.environ.setdefault('OAUTHLIB_INSECURE_TRANSPORT', '1')

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

CATEGORY_OPTIONS = ['Lifestyle', 'Beauty', 'F&B', 'Fashion', 'Health', 'Travel', 'Home Living']
PAYMENT_OPTIONS = ['Paid', 'Unpaid']
PLATFORM_OPTIONS = [
    'IG Story', 'IG Feeds', 'IG Reels', 'Threads',
    'TikTok Naughtysensei', 'TikTok mariannehanna',
]
STATUS_OPTIONS = [
    'On progress',
    'On approval',
    'On revision',
    'Waiting client brief',
    'Waiting product arrival',
    "Waiting client's payment",
    'DONE',
]
FINISHED_STATUS_OPTIONS = ['DONE']
FINISHED_STATUS_VALUES = {status.upper() for status in FINISHED_STATUS_OPTIONS}
INCOME_STATUS = 'DONE'
EXPENSE_CATEGORY_OPTIONS = ['Editor', 'Asisten', 'Transport', 'Peralatan', 'Software', 'Lain-lain']
MONTH_LABELS_ID = [
    'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
    'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'
]

# ============ DATABASE MODELS ============
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    google_id = db.Column(db.String(100), nullable=True)
    google_email = db.Column(db.String(200), nullable=True)
    google_access_token = db.Column(db.Text, nullable=True)
    google_refresh_token = db.Column(db.Text, nullable=True)
    google_token_expiry = db.Column(db.DateTime, nullable=True)
    konten = db.relationship('Konten', backref='author', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Konten(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    judul = db.Column(db.String(200), nullable=False)
    deskripsi = db.Column(db.Text, nullable=False)
    isi = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(120), nullable=True)
    brand = db.Column(db.String(120), nullable=True)
    campaign_project = db.Column(db.String(200), nullable=True)
    payment = db.Column(db.String(40), nullable=True)
    fee = db.Column(db.String(80), nullable=True)
    sow = db.Column(db.String(200), nullable=True)
    platform = db.Column(db.String(120), nullable=True)
    status = db.Column(db.String(80), nullable=True)
    deadline = db.Column(db.Date, nullable=True)
    product_knowledge = db.Column(db.Text, nullable=True)
    product_knowledge_link = db.Column(db.String(500), nullable=True)
    link_content = db.Column(db.String(500), nullable=True)
    note = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def deadline_state(self):
        if not self.deadline:
            return 'no-deadline'

        status = (self.status or '').upper()
        if status in FINISHED_STATUS_VALUES:
            return 'done'

        today = date.today()
        days_left = (self.deadline - today).days
        if days_left < 0:
            return 'overdue'
        if days_left <= 3:
            return 'due-critical'
        if days_left <= 5:
            return 'due-soon'
        return 'normal'

    @property
    def days_left(self):
        if not self.deadline:
            return None
        return (self.deadline - date.today()).days

    @property
    def deadline_text(self):
        if not self.deadline:
            return '-'
        return self.deadline.strftime('%d/%m/%Y')


class Pengeluaran(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tanggal = db.Column(db.Date, nullable=False)
    kategori = db.Column(db.String(80), nullable=False)
    deskripsi = db.Column(db.String(300), nullable=True)
    jumlah = db.Column(db.Integer, nullable=False, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Invoice(db.Model):
    __tablename__ = 'invoice'
    id = db.Column(db.Integer, primary_key=True)
    konten_id = db.Column(db.Integer, db.ForeignKey('konten.id', ondelete='CASCADE'), nullable=False, unique=True)
    invoice_number = db.Column(db.String(20), nullable=False)
    campaign_number = db.Column(db.String(10), nullable=False)
    first_downloaded_at = db.Column(db.DateTime, nullable=True)
    items_json = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    konten = db.relationship('Konten', backref=db.backref('invoice', uselist=False))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def parse_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except ValueError:
        return None


def parse_fee(fee_str):
    if not fee_str:
        return 0
    digits = re.sub(r'[^\d]', '', fee_str)
    return int(digits) if digits else 0


def is_finished_status(status):
    return (status or '').upper() in FINISHED_STATUS_VALUES


def format_month_label(month_key):
    year, month = month_key.split('-')
    return f'{MONTH_LABELS_ID[int(month) - 1]} {year}'


@app.template_filter('idr')
def idr_filter(amount):
    if not amount:
        return 'Rp 0'
    return 'Rp ' + f'{int(amount):,}'.replace(',', '.')


@app.template_filter('status_label')
def status_label_filter(status):
    if not status:
        return ''
    if str(status).upper() == 'DONE':
        return 'Done'
    return status


def form_text(name):
    return (request.form.get(name) or '').strip()


def apply_tracker_form(konten):
    konten.category = form_text('category')
    konten.brand = form_text('brand')
    konten.campaign_project = form_text('campaign_project')
    konten.payment = form_text('payment')
    konten.fee = form_text('fee')
    konten.sow = form_text('sow')
    platforms = request.form.getlist('platform')
    konten.platform = ', '.join(platforms) if platforms else ''
    konten.status = form_text('status')
    konten.deadline = parse_date(form_text('deadline'))
    konten.product_knowledge = form_text('product_knowledge')
    konten.product_knowledge_link = form_text('product_knowledge_link')
    konten.link_content = form_text('link_content')
    konten.note = form_text('note')

    # Keep the original CMS fields populated so older rows/templates remain compatible.
    konten.judul = konten.campaign_project or konten.brand or 'Campaign tanpa nama'
    konten.deskripsi = konten.note or konten.sow or '-'
    konten.isi = konten.product_knowledge or konten.link_content or konten.note or '-'


def validate_tracker_form():
    required_fields = {
        'category': 'Category',
        'brand': 'Brand',
        'campaign_project': 'Campaign/Project',
        'payment': 'Payment',
        'status': 'Status',
        'deadline': 'Deadline'
    }
    missing = [label for field, label in required_fields.items() if not form_text(field)]
    if not request.form.getlist('platform'):
        missing.append('Platform')
    if missing:
        return f"Field wajib diisi: {', '.join(missing)}."
    if not parse_date(form_text('deadline')):
        return 'Format deadline tidak valid.'
    return None


def tracker_options():
    return {
        'category_options': CATEGORY_OPTIONS,
        'payment_options': PAYMENT_OPTIONS,
        'platform_options': PLATFORM_OPTIONS,
        'status_options': STATUS_OPTIONS
    }


def ordered_tracker_query():
    from sqlalchemy import case
    done_last = case((Konten.status.in_(FINISHED_STATUS_OPTIONS), 1), else_=0)
    return Konten.query.filter_by(user_id=current_user.id).order_by(
        done_last,
        Konten.deadline.is_(None),
        Konten.deadline.asc(),
        Konten.created_at.desc()
    )


def due_soon_query():
    today = date.today()
    return Konten.query.filter(
        Konten.user_id == current_user.id,
        Konten.deadline >= today,
        Konten.deadline <= today + timedelta(days=5),
        ~Konten.status.in_(FINISHED_STATUS_OPTIONS)
    )


def build_income_context(user_id):
    from collections import defaultdict
    monthly_buckets = defaultdict(lambda: {'count': 0, 'total': 0})
    transfer_items = Konten.query.filter_by(user_id=user_id, status=INCOME_STATUS).all()

    for k in transfer_items:
        ref = k.deadline or (k.created_at.date() if k.created_at else date.today())
        key = ref.strftime('%Y-%m')
        monthly_buckets[key]['count'] += 1
        monthly_buckets[key]['total'] += parse_fee(k.fee)

    sorted_keys = sorted(monthly_buckets.keys(), reverse=True)
    monthly_income = [
        {
            'key': m,
            'year': m[:4],
            'month': m[5:7],
            'label': format_month_label(m),
            'count': monthly_buckets[m]['count'],
            'total': monthly_buckets[m]['total'],
        }
        for m in sorted_keys
    ]

    return {
        'monthly_income': monthly_income,
        'total_income': sum(monthly_buckets[m]['total'] for m in monthly_buckets),
        'income_total_campaigns': sum(monthly_buckets[m]['count'] for m in monthly_buckets),
        'income_years': sorted({m[:4] for m in monthly_buckets}, reverse=True),
        'income_months': [
            {'value': month, 'label': MONTH_LABELS_ID[int(month) - 1]}
            for month in sorted({m[5:7] for m in monthly_buckets})
        ]
    }


def distinct_values(column):
    rows = db.session.query(column).filter(
        Konten.user_id == current_user.id,
        column.isnot(None),
        column != ''
    ).distinct().order_by(column.asc()).all()
    return [row[0] for row in rows]


def distinct_platform_options():
    values = set(PLATFORM_OPTIONS)
    for raw_value in distinct_values(Konten.platform):
        for platform in raw_value.split(', '):
            platform = platform.strip()
            if platform:
                values.add(platform)
    return sorted(values)


def platform_match_condition(platform):
    return or_(
        Konten.platform == platform,
        Konten.platform.like(f'{platform}, %'),
        Konten.platform.like(f'%, {platform}, %'),
        Konten.platform.like(f'%, {platform}')
    )


def ensure_tracker_columns():
    inspector = inspect(db.engine)
    if not inspector.has_table('konten'):
        return

    existing_columns = {column['name'] for column in inspector.get_columns('konten')}
    columns_sql = {
        'category': 'ALTER TABLE konten ADD COLUMN category VARCHAR(120)',
        'brand': 'ALTER TABLE konten ADD COLUMN brand VARCHAR(120)',
        'campaign_project': 'ALTER TABLE konten ADD COLUMN campaign_project VARCHAR(200)',
        'payment': 'ALTER TABLE konten ADD COLUMN payment VARCHAR(40)',
        'fee': 'ALTER TABLE konten ADD COLUMN fee VARCHAR(80)',
        'sow': 'ALTER TABLE konten ADD COLUMN sow VARCHAR(200)',
        'platform': 'ALTER TABLE konten ADD COLUMN platform VARCHAR(120)',
        'status': 'ALTER TABLE konten ADD COLUMN status VARCHAR(80)',
        'deadline': 'ALTER TABLE konten ADD COLUMN deadline DATE',
        'product_knowledge': 'ALTER TABLE konten ADD COLUMN product_knowledge TEXT',
        'product_knowledge_link': 'ALTER TABLE konten ADD COLUMN product_knowledge_link VARCHAR(500)',
        'link_content': 'ALTER TABLE konten ADD COLUMN link_content VARCHAR(500)',
        'note': 'ALTER TABLE konten ADD COLUMN note TEXT'
    }

    for column_name, statement in columns_sql.items():
        if column_name not in existing_columns:
            db.session.execute(text(statement))

    db.session.execute(text("""
        UPDATE konten
        SET
            campaign_project = COALESCE(campaign_project, judul),
            note = COALESCE(note, deskripsi),
            product_knowledge = COALESCE(product_knowledge, isi),
            category = COALESCE(category, 'General'),
            payment = COALESCE(payment, 'Paid'),
            platform = COALESCE(platform, 'Instagram'),
            status = COALESCE(status, 'On progress')
    """))
    db.session.commit()


def ensure_user_columns():
    inspector = inspect(db.engine)
    if not inspector.has_table('user'):
        return
    existing = {col['name'] for col in inspector.get_columns('user')}
    migrations = {
        'google_id': 'ALTER TABLE user ADD COLUMN google_id VARCHAR(100)',
        'google_email': 'ALTER TABLE user ADD COLUMN google_email VARCHAR(200)',
        'google_access_token': 'ALTER TABLE user ADD COLUMN google_access_token TEXT',
        'google_refresh_token': 'ALTER TABLE user ADD COLUMN google_refresh_token TEXT',
        'google_token_expiry': 'ALTER TABLE user ADD COLUMN google_token_expiry DATETIME',
    }
    for col, sql in migrations.items():
        if col not in existing:
            db.session.execute(text(sql))
    db.session.commit()


def get_google_flow():
    from google_auth_oauthlib.flow import Flow
    redirect_uri = url_for('google_callback', _external=True)
    if os.path.exists(_CREDS_FILE):
        return Flow.from_client_secrets_file(
            _CREDS_FILE,
            scopes=GOOGLE_SCOPES,
            redirect_uri=redirect_uri,
        )
    return Flow.from_client_config(
        {"web": {
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [redirect_uri],
        }},
        scopes=GOOGLE_SCOPES,
        redirect_uri=redirect_uri,
    )


def get_drive_service(user):
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request as GoogleRequest
    from googleapiclient.discovery import build

    creds = Credentials(
        token=user.google_access_token,
        refresh_token=user.google_refresh_token,
        token_uri='https://oauth2.googleapis.com/token',
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        scopes=GOOGLE_SCOPES,
    )
    if creds.expired and creds.refresh_token:
        creds.refresh(GoogleRequest())
        user.google_access_token = creds.token
        if creds.expiry:
            user.google_token_expiry = creds.expiry
        db.session.commit()
    return build('drive', 'v3', credentials=creds)


# ============ ROUTES ============
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')

        if not username or not email or not password:
            flash('Semua field harus diisi!', 'danger')
            return redirect(url_for('register'))

        if password != password_confirm:
            flash('Password tidak cocok!', 'danger')
            return redirect(url_for('register'))

        if User.query.filter_by(username=username).first():
            flash('Username sudah terdaftar!', 'danger')
            return redirect(url_for('register'))

        if User.query.filter_by(email=email).first():
            flash('Email sudah terdaftar!', 'danger')
            return redirect(url_for('register'))

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('Akun berhasil dibuat! Silakan login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('Username dan password harus diisi!', 'danger')
            return redirect(url_for('login'))

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            flash(f'Selamat datang, {user.username}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Username atau password salah!', 'danger')

    return render_template('login.html', google_configured=bool(GOOGLE_CLIENT_ID))


@app.route('/dashboard')
@login_required
def dashboard():
    from sqlalchemy import case as sa_case
    page = request.args.get('page', 1, type=int)
    q    = request.args.get('q', '').strip()
    sort = request.args.get('sort', 'deadline')

    query = Konten.query.filter_by(user_id=current_user.id)

    if q:
        like = f'%{q}%'
        query = query.filter(or_(
            Konten.brand.ilike(like),
            Konten.campaign_project.ilike(like),
            Konten.category.ilike(like),
            Konten.status.ilike(like),
        ))

    if sort == 'brand':
        query = query.order_by(Konten.brand.asc(), Konten.created_at.desc())
    elif sort == 'status':
        query = query.order_by(Konten.status.asc(), Konten.deadline.asc())
    elif sort == 'newest':
        query = query.order_by(Konten.created_at.desc())
    else:
        done_last = sa_case((Konten.status.in_(FINISHED_STATUS_OPTIONS), 1), else_=0)
        query = query.order_by(done_last, Konten.deadline.is_(None), Konten.deadline.asc(), Konten.created_at.desc())

    konten_list   = query.paginate(page=page, per_page=20)
    total_konten  = Konten.query.filter_by(user_id=current_user.id).count()
    due_soon_count = due_soon_query().count()
    done_count = Konten.query.filter(
        Konten.user_id == current_user.id,
        Konten.status.in_(FINISHED_STATUS_OPTIONS)
    ).count()

    return render_template(
        'dashboard.html',
        konten_list=konten_list,
        total_konten=total_konten,
        due_soon_count=due_soon_count,
        done_count=done_count,
        q=q,
        sort=sort,
    )


@app.route('/pendapatan')
@login_required
def pendapatan():
    return render_template('pendapatan.html', **build_income_context(current_user.id))


def _next_invoice_number(user_id):
    year = datetime.now().year
    count = Invoice.query.join(Konten).filter(
        Konten.user_id == user_id,
        Invoice.invoice_number.like(f'INV-{year}-%')
    ).count()
    return f'INV-{year}-{count + 1:04d}'


def _next_campaign_number(user_id):
    count = Invoice.query.join(Konten).filter(Konten.user_id == user_id).count()
    return f'{count + 1:04d}'


def _default_invoice_items(konten):
    rate = parse_fee(konten.fee) if is_finished_status(konten.status) else 0
    return [{'sow': konten.sow or '', 'platform': konten.platform or '', 'qty': 1, 'rate': rate}]


@app.route('/invoice/<int:konten_id>', methods=['GET'])
@login_required
def show_invoice(konten_id):
    k = Konten.query.filter_by(id=konten_id, user_id=current_user.id).first_or_404()
    inv = Invoice.query.filter_by(konten_id=konten_id).first()
    if not inv:
        inv = Invoice(
            konten_id=konten_id,
            invoice_number=_next_invoice_number(current_user.id),
            campaign_number=_next_campaign_number(current_user.id)
        )
        db.session.add(inv)
        db.session.commit()
    items = _json.loads(inv.items_json) if inv.items_json else _default_invoice_items(k)
    return render_template('invoice.html', konten=k, invoice=inv, items=items,
                           creator_name=current_user.username.replace('.', ' ').title())


@app.route('/invoice/<int:konten_id>/save', methods=['POST'])
@login_required
def save_invoice(konten_id):
    k = Konten.query.filter_by(id=konten_id, user_id=current_user.id).first_or_404()
    inv = Invoice.query.filter_by(konten_id=konten_id).first_or_404()
    sows = request.form.getlist('sow[]')
    platforms = request.form.getlist('platform[]')
    qtys = request.form.getlist('qty[]')
    rates = request.form.getlist('rate[]')
    items = []
    for i in range(len(sows)):
        raw_rate = rates[i] if i < len(rates) else '0'
        items.append({
            'sow': sows[i] if i < len(sows) else '',
            'platform': platforms[i] if i < len(platforms) else '',
            'qty': max(1, int(qtys[i])) if i < len(qtys) and qtys[i].isdigit() else 1,
            'rate': int(re.sub(r'[^\d]', '', raw_rate)) if raw_rate else 0
        })
    inv.items_json = _json.dumps(items)
    if not inv.first_downloaded_at:
        inv.first_downloaded_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'ok': True})


@app.route('/konten/buat', methods=['GET', 'POST'])
@login_required
def buat_konten():
    if request.method == 'POST':
        error = validate_tracker_form()
        if error:
            flash(error, 'danger')
            return redirect(url_for('buat_konten'))

        konten = Konten(judul='', deskripsi='', isi='', user_id=current_user.id)
        apply_tracker_form(konten)
        db.session.add(konten)
        db.session.commit()

        flash('Campaign berhasil dibuat!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('buat_konten.html', **tracker_options())


@app.route('/konten/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_konten(id):
    konten = Konten.query.get_or_404(id)
    
    if konten.user_id != current_user.id:
        flash('Anda tidak memiliki akses ke konten ini!', 'danger')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        error = validate_tracker_form()
        if error:
            flash(error, 'danger')
            return redirect(url_for('edit_konten', id=id))

        apply_tracker_form(konten)
        konten.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Campaign berhasil diperbarui!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('edit_konten.html', konten=konten, **tracker_options())


@app.route('/report')
@login_required
def report():
    query = ordered_tracker_query()
    filters = {
        'start_date': request.args.get('start_date', '').strip(),
        'end_date': request.args.get('end_date', '').strip(),
        'category': request.args.get('category', '').strip(),
        'brand': request.args.get('brand', '').strip(),
        'payment': request.args.get('payment', '').strip(),
        'platform': [item.strip() for item in request.args.getlist('platform') if item.strip()],
        'status': request.args.get('status', '').strip()
    }

    start_date = parse_date(filters['start_date'])
    end_date = parse_date(filters['end_date'])
    if start_date:
        query = query.filter(Konten.deadline >= start_date)
    if end_date:
        query = query.filter(Konten.deadline <= end_date)
    if filters['category']:
        query = query.filter(Konten.category == filters['category'])
    if filters['brand']:
        query = query.filter(Konten.brand == filters['brand'])
    if filters['payment']:
        query = query.filter(Konten.payment == filters['payment'])
    if filters['platform']:
        platform_conditions = [platform_match_condition(platform) for platform in filters['platform']]
        query = query.filter(or_(*platform_conditions))
    if filters['status']:
        query = query.filter(Konten.status == filters['status'])

    results = query.all()
    report_options = tracker_options()
    report_options.update({
        'brand_options': distinct_values(Konten.brand),
        'category_options': sorted(set(CATEGORY_OPTIONS + distinct_values(Konten.category))),
        'platform_options': distinct_platform_options()
    })

    return render_template(
        'report.html',
        results=results,
        filters=filters,
        total_results=len(results),
        due_soon_count=sum(1 for item in results if item.deadline_state == 'due-soon'),
        done_count=sum(1 for item in results if is_finished_status(item.status)),
        **report_options
    )


@app.route('/konten/<int:id>/delete', methods=['POST'])
@login_required
def delete_konten(id):
    konten = Konten.query.get_or_404(id)
    
    if konten.user_id != current_user.id:
        flash('Anda tidak memiliki akses ke konten ini!', 'danger')
        return redirect(url_for('dashboard'))

    db.session.delete(konten)
    db.session.commit()
    flash('Konten berhasil dihapus!', 'success')
    return redirect(url_for('dashboard'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Anda telah logout.', 'info')
    return redirect(url_for('login'))


@app.route('/auth/google')
def google_login():
    if not GOOGLE_CLIENT_ID:
        flash('Google login belum dikonfigurasi oleh admin.', 'danger')
        return redirect(url_for('login'))
    flow = get_google_flow()
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        prompt='consent',
        include_granted_scopes='true',
    )
    session['google_oauth_state'] = state
    return redirect(authorization_url)


@app.route('/auth/google/callback')
def google_callback():
    if not GOOGLE_CLIENT_ID:
        return redirect(url_for('login'))

    if request.args.get('error'):
        flash('Login Google dibatalkan.', 'warning')
        return redirect(url_for('login'))

    if request.args.get('state') != session.pop('google_oauth_state', None):
        flash('Terjadi masalah saat login Google. Coba lagi.', 'danger')
        return redirect(url_for('login'))

    try:
        flow = get_google_flow()
        flow.fetch_token(authorization_response=request.url)
        credentials = flow.credentials

        from googleapiclient.discovery import build
        info_service = build('oauth2', 'v2', credentials=credentials)
        user_info = info_service.userinfo().get().execute()

        google_id = user_info.get('id')
        google_email = user_info.get('email', '')
        google_name = user_info.get('name', '')

        # Find existing user by google_id, then by email
        user = User.query.filter_by(google_id=google_id).first()
        if not user:
            user = User.query.filter_by(email=google_email).first()
        if not user:
            base = google_email.split('@')[0].replace('.', '_').replace('-', '_')
            username = base
            counter = 1
            while User.query.filter_by(username=username).first():
                username = f'{base}_{counter}'
                counter += 1
            user = User(username=username, email=google_email,
                        password=generate_password_hash(str(uuid.uuid4())))
            db.session.add(user)

        user.google_id = google_id
        user.google_email = google_email
        user.google_access_token = credentials.token
        if credentials.refresh_token:
            user.google_refresh_token = credentials.refresh_token
        if credentials.expiry:
            user.google_token_expiry = credentials.expiry
        db.session.commit()

        login_user(user)
        flash(f'Selamat datang, {user.username}! 🌸', 'success')
        return redirect(url_for('dashboard'))

    except Exception as e:
        flash('Login Google gagal. Silakan coba lagi.', 'danger')
        return redirect(url_for('login'))


@app.route('/drive/upload', methods=['POST'])
@login_required
def drive_upload():
    if not current_user.google_access_token:
        return jsonify({'error': 'Kamu belum login dengan Google. Silakan logout lalu login ulang menggunakan akun Google.'}), 403

    if 'file' not in request.files:
        return jsonify({'error': 'Tidak ada file yang dikirim.'}), 400

    file = request.files['file']
    if not file or file.filename == '':
        return jsonify({'error': 'File kosong.'}), 400

    try:
        import io
        from googleapiclient.http import MediaIoBaseUpload

        drive_service = get_drive_service(current_user)

        # Find or create "project-campaign" folder
        folder_name = 'project-campaign'
        res = drive_service.files().list(
            q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false",
            fields='files(id)',
            pageSize=1,
        ).execute()
        folders = res.get('files', [])
        if folders:
            folder_id = folders[0]['id']
        else:
            folder = drive_service.files().create(
                body={'name': folder_name, 'mimeType': 'application/vnd.google-apps.folder'},
                fields='id',
            ).execute()
            folder_id = folder['id']

        # Upload file into the folder
        content = file.read()
        mimetype = file.content_type or 'application/octet-stream'
        media = MediaIoBaseUpload(io.BytesIO(content), mimetype=mimetype, resumable=True)
        uploaded = drive_service.files().create(
            body={'name': file.filename, 'parents': [folder_id]},
            media_body=media,
            fields='id',
        ).execute()

        file_id = uploaded['id']
        drive_service.permissions().create(
            fileId=file_id,
            body={'type': 'anyone', 'role': 'reader'},
        ).execute()

        link = f'https://drive.google.com/file/d/{file_id}/view?usp=sharing'
        return jsonify({'link': link, 'filename': file.filename})

    except Exception as e:
        return jsonify({'error': f'Upload gagal: {str(e)}'}), 500


@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)


@app.route('/pengeluaran')
@login_required
def pengeluaran():
    from collections import defaultdict
    items = Pengeluaran.query.filter_by(user_id=current_user.id).order_by(
        Pengeluaran.tanggal.desc()
    ).all()
    monthly_buckets = defaultdict(lambda: {'count': 0, 'total': 0})
    for item in items:
        key = item.tanggal.strftime('%Y-%m')
        monthly_buckets[key]['count'] += 1
        monthly_buckets[key]['total'] += item.jumlah
    sorted_keys = sorted(monthly_buckets.keys(), reverse=True)[:6]
    monthly_expense = [
        {
            'key': k,
            'label': datetime.strptime(k, '%Y-%m').strftime('%B %Y'),
            'count': monthly_buckets[k]['count'],
            'total': monthly_buckets[k]['total'],
        }
        for k in sorted_keys
    ]
    total_all = sum(item.jumlah for item in items)
    return render_template('pengeluaran.html',
        items=items,
        monthly_expense=monthly_expense,
        total_all=total_all,
        category_options=EXPENSE_CATEGORY_OPTIONS
    )


@app.route('/pengeluaran/buat', methods=['GET', 'POST'])
@login_required
def buat_pengeluaran():
    if request.method == 'POST':
        tanggal = parse_date((request.form.get('tanggal') or '').strip())
        kategori = (request.form.get('kategori') or '').strip()
        deskripsi = (request.form.get('deskripsi') or '').strip()
        jumlah_str = re.sub(r'[^\d]', '', request.form.get('jumlah', ''))
        jumlah = int(jumlah_str) if jumlah_str else 0
        if not tanggal or not kategori or jumlah <= 0:
            flash('Tanggal, kategori, dan jumlah wajib diisi.', 'danger')
            return redirect(url_for('buat_pengeluaran'))
        item = Pengeluaran(tanggal=tanggal, kategori=kategori,
                           deskripsi=deskripsi, jumlah=jumlah,
                           user_id=current_user.id)
        db.session.add(item)
        db.session.commit()
        flash('Pengeluaran berhasil ditambahkan!', 'success')
        return redirect(url_for('pengeluaran'))
    return render_template('buat_pengeluaran.html',
        category_options=EXPENSE_CATEGORY_OPTIONS,
        today=date.today().isoformat()
    )


@app.route('/pengeluaran/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_pengeluaran(id):
    item = Pengeluaran.query.get_or_404(id)
    if item.user_id != current_user.id:
        flash('Tidak ada akses.', 'danger')
        return redirect(url_for('pengeluaran'))
    if request.method == 'POST':
        tanggal = parse_date((request.form.get('tanggal') or '').strip())
        kategori = (request.form.get('kategori') or '').strip()
        deskripsi = (request.form.get('deskripsi') or '').strip()
        jumlah_str = re.sub(r'[^\d]', '', request.form.get('jumlah', ''))
        jumlah = int(jumlah_str) if jumlah_str else 0
        if not tanggal or not kategori or jumlah <= 0:
            flash('Tanggal, kategori, dan jumlah wajib diisi.', 'danger')
            return redirect(url_for('edit_pengeluaran', id=id))
        item.tanggal = tanggal
        item.kategori = kategori
        item.deskripsi = deskripsi
        item.jumlah = jumlah
        db.session.commit()
        flash('Pengeluaran berhasil diperbarui!', 'success')
        return redirect(url_for('pengeluaran'))
    return render_template('edit_pengeluaran.html',
        item=item,
        category_options=EXPENSE_CATEGORY_OPTIONS
    )


@app.route('/pengeluaran/<int:id>/delete', methods=['POST'])
@login_required
def delete_pengeluaran(id):
    item = Pengeluaran.query.get_or_404(id)
    if item.user_id != current_user.id:
        flash('Tidak ada akses.', 'danger')
        return redirect(url_for('pengeluaran'))
    db.session.delete(item)
    db.session.commit()
    flash('Pengeluaran berhasil dihapus!', 'success')
    return redirect(url_for('pengeluaran'))


def init_db():
    db.create_all()
    ensure_tracker_columns()
    ensure_user_columns()
    default_user = User.query.filter_by(username='marianne.hanna').first()
    if not default_user:
        default_user = User(
            username='marianne.hanna',
            email='marianne.hanna@email.com'
        )
        default_user.set_password('TuhanMemberkati31!')
        db.session.add(default_user)
        db.session.commit()
        print("✅ Default account created: marianne.hanna")


with app.app_context():
    init_db()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
