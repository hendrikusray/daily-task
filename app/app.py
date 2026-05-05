from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date, datetime, timedelta
from sqlalchemy import inspect, text

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///konten.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

CATEGORY_OPTIONS = ['Lifestyle', 'Beauty', 'F&B', 'Fashion', 'Health', 'Travel', 'Home Living']
PAYMENT_OPTIONS = ['Paid', 'Unpaid']
PLATFORM_OPTIONS = ['Reels', 'Instagram', 'TikTok', 'YouTube', 'Shopee', 'Blog', 'Story']
STATUS_OPTIONS = [
    'On progress',
    'On approval',
    'On revision',
    'Waiting client brief',
    'Waiting product arrival',
    "Waiting client's payment",
    'DONE'
]

# ============ DATABASE MODELS ============
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
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
        if status == 'DONE':
            return 'done'

        today = date.today()
        days_left = (self.deadline - today).days
        if days_left < 0:
            return 'overdue'
        if days_left <= 5:
            return 'due-soon'
        return 'normal'

    @property
    def deadline_text(self):
        if not self.deadline:
            return '-'
        return self.deadline.strftime('%d/%m/%Y')


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


def form_text(name):
    return (request.form.get(name) or '').strip()


def apply_tracker_form(konten):
    konten.category = form_text('category')
    konten.brand = form_text('brand')
    konten.campaign_project = form_text('campaign_project')
    konten.payment = form_text('payment')
    konten.fee = form_text('fee')
    konten.sow = form_text('sow')
    konten.platform = form_text('platform')
    konten.status = form_text('status')
    konten.deadline = parse_date(form_text('deadline'))
    konten.product_knowledge = form_text('product_knowledge')
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
        'platform': 'Platform',
        'status': 'Status',
        'deadline': 'Deadline'
    }
    missing = [label for field, label in required_fields.items() if not form_text(field)]
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
    return Konten.query.filter_by(user_id=current_user.id).order_by(
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
        Konten.status != 'DONE'
    )


def distinct_values(column):
    rows = db.session.query(column).filter(
        Konten.user_id == current_user.id,
        column.isnot(None),
        column != ''
    ).distinct().order_by(column.asc()).all()
    return [row[0] for row in rows]


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

    return render_template('login.html')


@app.route('/dashboard')
@login_required
def dashboard():
    page = request.args.get('page', 1, type=int)
    konten_list = ordered_tracker_query().paginate(page=page, per_page=25)
    total_konten = Konten.query.filter_by(user_id=current_user.id).count()
    due_soon_count = due_soon_query().count()
    done_count = Konten.query.filter_by(user_id=current_user.id, status='DONE').count()
    
    return render_template(
        'dashboard.html',
        konten_list=konten_list,
        total_konten=total_konten,
        due_soon_count=due_soon_count,
        done_count=done_count
    )


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
        'platform': request.args.get('platform', '').strip(),
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
        query = query.filter(Konten.platform == filters['platform'])
    if filters['status']:
        query = query.filter(Konten.status == filters['status'])

    results = query.all()
    report_options = tracker_options()
    report_options.update({
        'brand_options': distinct_values(Konten.brand),
        'category_options': sorted(set(CATEGORY_OPTIONS + distinct_values(Konten.category))),
        'platform_options': sorted(set(PLATFORM_OPTIONS + distinct_values(Konten.platform)))
    })

    return render_template(
        'report.html',
        results=results,
        filters=filters,
        total_results=len(results),
        due_soon_count=sum(1 for item in results if item.deadline_state == 'due-soon'),
        done_count=sum(1 for item in results if (item.status or '').upper() == 'DONE'),
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


@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        ensure_tracker_columns()
        
        # Create default account if not exists
        default_user = User.query.filter_by(username='marianne.hanna').first()
        if not default_user:
            default_user = User(
                username='marianne.hanna',
                email='marianne.hanna@email.com'
            )
            default_user.set_password('TuhanMemberkati31!')
            db.session.add(default_user)
            db.session.commit()
            print("✅ Default account created:")
            print("   Username: marianne.hanna")
            print("   Password: TuhanMemberkati31!")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
