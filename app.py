# ======= IMPORTAÇÕES ========

# Flask: framework web principal
# render_template: renderiza arquivos HTML da pasta templates/
# request: acessa dados enviados pelo cliente (formulários, query strings, etc.)
# flash: exibe mensagens temporárias (feedback ao usuário)
# redirect, url_for: redirecionam para outras rotas de forma dinâmica
from flask import Flask, render_template, request, flash, redirect, url_for
# SQLAlchemy: ORM (Object-Relational Mapper) que traduz classes Python em tabelas SQL
from flask_sqlalchemy import SQLAlchemy
# Werkzeug: biblioteca de segurança para hashing de senhas
# generate_password_hash: cria um hash criptografado a partir da senha
# check_password_hash: verifica se a senha digitada corresponde ao hash salvo
from werkzeug.security import generate_password_hash, check_password_hash
# Flask-Login: gerencia sessões de usuário (login/logout)
# LoginManager: configura o sistema de login
# UserMixin: fornece implementações padrão para métodos como is_authenticated, get_id, etc.
# login_user: cria a sessão para um usuário autenticado
# logout_user: destrói a sessão do usuário
# login_required: decorador que protege rotas exigindo login
# current_user: objeto que representa o usuário logado (acessível em qualquer rota/template)
from flask_login import  LoginManager, UserMixin, login_user, logout_user, login_required, current_user
# os: módulo nativo do python para interagir com o sistema operacional
import os 
# dotenv: mantém privado os dados dentro do arquivo .env
from dotenv import load_dotenv
# flask_wtf e CSRFProtect: Proteção aos forms contra ataques e integra validação dos dados 
from flask_wtf import CSRFProtect
from flask_migrate import Migrate
from datetime import timedelta, datetime, date


load_dotenv()

IS_PRODUCTION = os.environ.get('APP_ENV') == 'production'

app = Flask(__name__)

secret_key = os.environ.get('SECRET_KEY')
if not secret_key:
    if IS_PRODUCTION:
        raise RuntimeError('SECRET_KEY não definida em produção')
    secret_key = 'dev-fallback-key'

app.config['SECRET_KEY'] = secret_key
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=14)

app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['REMEMBER_COOKIE_HTTPONLY'] = True
app.config['REMEMBER_COOKIE_SAMESITE'] = 'Lax'

if IS_PRODUCTION:
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['REMEMBER_COOKIE_SECURE'] = True


csrf = CSRFProtect(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///meu_banco.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['TEMPLATES_AUTO_RELOAD'] = True

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(100), nullable=True)

    # Recebe a senha, gera o hash e armazena em password_hash
    def set_password(self, senha):
        self.password_hash = generate_password_hash(senha)

    # Verifica se a senha corresponde ao hash que foi armazenado
    def check_password(self, senha):
        return check_password_hash(self.password_hash, senha)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    priority = db.Column(db.String(20), default='Média')
    due_date = db.Column(db.Date, nullable=True)

    #Chave estrangeira, garante que toda tarefa tem um usuário
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Acessa as tarefas de um usuário
    user = db.relationship('User', backref=db.backref('tasks', lazy=True))

    def __repr__(self):
        return f'<Task {self.title}>'


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor, faça login para acessar esta página.'


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

PRIORITIES = ('Baixa', 'Média', 'Alta')

def get_task_form_data():
    title = (request.form.get('title') or '').strip()
    description = (request.form.get('description') or '').strip()
    priority = request.form.get('priority')
    if priority not in PRIORITIES:
        priority = 'Média'
    return title, description or None, priority

def validate_title(title):
    if not title:
        return 'O título é obrigatório'
    if len(title) > 200:
        return 'O título deve ter no máximo 200 caracteres'
    return None

def parse_due_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except ValueError:
        return None

with app.app_context():
    db.create_all()

    admin_email = os.environ.get('ADMIN_EMAIL', 'admin@email.com').strip().lower()
    admin_password = os.environ.get('ADMIN_PASSWORD')

    if admin_password and not User.query.filter_by(email=admin_email).first():
        admin = User(email=admin_email, name='Administrador')
        admin.set_password(admin_password)
        db.session.add(admin)
        db.session.commit()


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = (request.form.get('name') or '').strip()
        email = (request.form.get('email') or '').strip().lower()
        password = request.form.get('password') or ''
        confirm = request.form.get('confirm_password') or ''

        if not email or not password:
            flash('Preencha todos os campos obrigatórios', 'danger')
            return redirect(url_for('register'))

        if len(email) > 120 or len(name) > 100:
            flash('Nome ou e-mail excedem o tamanho máximo permitido', 'danger')
            return redirect(url_for('register'))

        if len(password) < 6:
            flash('A senha deve ter no mínimo 6 caracteres', 'danger')
            return redirect(url_for('register'))
        
        if password != confirm:
            flash('As senhas não são iguais', 'danger')
            return redirect(url_for('register'))

        if User.query.filter_by(email=email).first():
            flash('Este email já está cadastrado', 'danger')
            return redirect(url_for('register'))


        new_user = User(email=email, name=name or None)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()


        flash('Conta criada com sucesso! Faça login', 'success')
        return redirect(url_for('login'))


    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email').lower().strip()
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        user = User.query.filter_by(email=email).first()

        # Verifica se o usuário existe e se a senha está correta
        if user and user.check_password(password):
            """ login_user(user) cria a sessão e mantém o user logado entre requisições"""
            login_user(user, remember=remember)
            flash('Login realizado!', 'success')
            return redirect(url_for('dashboard'))
        else: 
            flash('Email ou senha inválidos', 'danger')
            return redirect(url_for('login'))        
    return render_template('index.html')


@app.route('/dashboard')
@login_required
def dashboard():
    tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.created_at.desc()).all()
    return render_template('dashboard.html', tasks=tasks, today=date.today())

@app.route('/task/new', methods=['GET', 'POST'])
@login_required
def new_task():
    if request.method == 'POST':
        title, description, priority = get_task_form_data()

        error = validate_title(title)
        if error:
            flash(error, 'danger')
            return redirect(url_for('new_task'))

        task = Task(title=title, description=description,
                    priority=priority, due_date=parse_due_date(request.form.get('due_date')) ,user_id=current_user.id)
        db.session.add(task)
        db.session.commit()

        flash('Tarefa criada com sucesso!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('task_form.html', task=None)

@app.route('/task/edit/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)

    # Impede que um usuário edite tarefas de outro usuário
    if task.user_id != current_user.id:
        flash('Você não tem permissão para editar esta tarefa', 'danger')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        title, description, priority = get_task_form_data()

        error = validate_title(title)
        if error:
            flash(error, 'danger')
            return redirect(url_for('edit_task', task_id=task.id))

        task.title = title
        task.description = description
        task.priority = priority
        task.due_date = parse_due_date(request.form.get('due_date'))
        task.completed = bool(request.form.get('completed'))

        db.session.commit()
        flash('Tarefa atualizada', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('task_form.html', task=task)


@app.route('/task/delete/<int:task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)

    # Impede que um usuário delete uma tarefa de outro usuário
    if task.user_id != current_user.id:
        flash('Você não tem permissão para deletar esta tarefa', 'danger')
        return redirect(url_for('dashboard'))

    db.session.delete(task)
    db.session.commit()
    flash('Tarefa removida', 'success')
    return redirect(url_for('dashboard'))


@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    flash('Você saiu', 'info')
    return redirect (url_for('login'))


@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403

@app.errorhandler(500)
def internal_error(e):
    db.session.rollback()
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run(debug=os.environ.get('FLASK_DEBUG', '0') == '1')