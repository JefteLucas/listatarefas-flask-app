# IMPORTAÇÕES

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

# Configuração do app

app = Flask(__name__)
# Chave secreta
app.config['SECRET_KEY'] = 'JUMA'


# Configuração do banco de dados

# Cria um arquivo .db na raiz do projeto
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///meu_banco.db'

# Desativa rastreamento de modificações, melhora a perfomance e elimina warnings
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Recarrega templates automaticamente sem reiniciar o servidor
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Inicialização do banco de dados
#Cria a instância do SQLAlchemy vinculada ao app flask
db = SQLAlchemy(app)


# Modelos de dados (Tabelas do banco)

# Estrutura do banco de dados que recebe dados do usuário cadastrado
# Modelo que representa um usuário do sistema
class User(db.Model, UserMixin): # db.model(mapeamento sql) e User Mixin(método do flask-login)
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

# Tabela de tarefas
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    priority = db.Column(db.String(20), default='Média')

    #Chave estrangeira, garante que toda tarefa tem um usuário
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Acessa as tarefas de um usuário
    user = db.relationship('User', backref=db.backref('tasks', lazy=True))

    def __repr__(self):
        return f'<Task {self.title}>'

# Configurações do flask-login (Gerenciamento de sessão)
login_manager = LoginManager()
login_manager.init_app(app)

# Define a rota para onde o usuário será redirecionado quando tentar acessar uma página sem estar logado
login_manager.login_view = 'login'

# Exibe a mensagem ao redirecionar para a página de login
login_manager.login_message = 'Por favor, faça login para acessar esta página.'

# Função obrigatória do flask-login, recebe o id do user e armazena na sessão retornando o objeto user
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


#Criação das tabelas e do usuário admin

#Cria usuário admin
with app.app_context():
    db.create_all()
    if not User.query.filter_by(email='admin@email.com').first():
        admin = User(email='admin@email.com', name= 'Administrador')
        admin.set_password('123456')
        db.session.add(admin)
        db.session.commit()

# Rotas públicas, acesso generalizado

# Rota para o index - Página inicial exibe o form de login
@app.route('/')
def index():
    return render_template('index.html')

# Registro de novos usuários - Página de cadastro
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm_password')

        # Validações de campos obrigatórios
        if not email or not password:
            flash('Preencha todos os campos obrigatórios', 'danger')
            return redirect(url_for('register'))

        # Validação de confirmação de senha
        if password != confirm:
            flash('As senhas não são iguais', 'danger')
            return redirect(url_for('register'))

        # Validação de email único
        if User.query.filter_by(email=email).first():
            flash('Este email já está cadastrado', 'danger')
            return redirect(url_for('register'))

        # Cria novo usuário
        new_user = User(email=email, name=name)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash('Conta criada com sucesso! Faça login', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# Rota de login - Página de login 
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        # Verifica se o usuário existe e se a senha está correta
        if user and user.check_password(password):
            """ login_user(user) cria a sessão e mantém o user logado entre requisições"""
            login_user(user)
            flash('Login realizado!', 'success')
            return redirect(url_for('dashboard'))
        else: 
            flash('Email ou senha inválidos', 'danger')
            return redirect(url_for('login'))        
    return render_template('index.html')


# Rotas protegidas com login_required (Exigem autenticação com @login_required)

# Painel pricipal do usuário
@app.route('/dashboard')
@login_required
def dashboard():
    """ Busca as tarefas filtrando pelo user_id do usuário logado"""
    tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.created_at.desc()).all()
    return render_template('dashboard.html', tasks=tasks)

#Cria novas tarefas para o usuário logado
@app.route('/task/new', methods=['GET', 'POST'])
@login_required
def new_task():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        priority = request.form.get('priority')

        if not title:
            flash('O título é obrigatório', 'danger')
            return redirect(url_for('new_task'))

        task = Task(title=title, description=description, priority=priority, user_id=current_user.id)
        db.session.add(task)
        db.session.commit()

        flash('Tarefa criada com sucesso!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('task_form.html', task=None) 

# Edita tarefas existente
@app.route('/task/edit/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)

    # Impede que um usuário edite tarefas de outro usuário
    if task.user_id != current_user.id:
        flash('Você não tem permissão para editar esta tarefa', 'danger')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        task.title = request.form.get('title')
        task.description = request.form.get('description')
        task.priority = request.form.get('priority')
        task.completed = True if request.form.get('completed') else False

        db.session.commit()
        flash('Tarefa atualizada', 'success')
        return redirect(url_for('dashboard'))

    return render_template('task_form.html', task=task)

# Remove uma tarefa do banco de dados
@app.route('/task/delete/<int:task_id>')
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

# Redireciona para página de login quando o logout é feito por usuário logado
@app.route('/logout')
@login_required
def logout():
    print("Rota logout acessada")
    flash('Você saiu', 'info')
    return redirect (url_for('login'))

# Execução da aplicação em desenvolvimento
if __name__ == '__main__':
    app.run(debug=True) # recarrega a página automaticamente em caso de erro 404