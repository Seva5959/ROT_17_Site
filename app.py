from flask import Flask, render_template, request, redirect, url_for, flash
from models import CodeStatus, CORRECT_ANSWERS, db, UserProgress, User
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime

app = Flask(__name__)
app.secret_key = '8b9f28a56878e86e8eef3296ff8b050e2a23e2941bd555cc'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///codes.db'
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


with app.app_context():
    db.create_all()
    if CodeStatus.query.count() == 0:
        for i in range(1, 18):
            db.session.add(CodeStatus(number=i))
        db.session.commit()


@app.route('/', endpoint='main_index')
@login_required
def index():
    # Здесь мы получаем все записи о прогрессе пользователя
    progress = UserProgress.query.filter_by(user_id=current_user.id).all()
    # Получаем статусы всех кодов
    codes = CodeStatus.query.all()
    # Создаем словарь с информацией о решении для каждого кода
    solved_dict = {p.code_id: p.solved for p in progress}
    # Обновляем статус решения для каждого кода
    for code in codes:
        code.solved = solved_dict.get(code.id, False)

    return render_template('index.html', codes=codes, answers=CORRECT_ANSWERS)


@app.route('/check/<int:code_id>', methods=['POST'])
@login_required
def check(code_id):
    user_input = request.form['decoded_text'].strip()
    # Получаем код по его номеру в базе
    code = CodeStatus.query.get(code_id)
    if not code:
        flash('❌ Код не найден')
        return redirect(url_for('main_index'))
    correct_answer = CORRECT_ANSWERS.get(code.number)  # Используем code.number вместо code_id
    progress = UserProgress.query.filter_by(
        user_id=current_user.id,
        code_id=code_id
    ).first()

    if not progress:
        progress = UserProgress(
            user_id=current_user.id,
            code_id=code_id
        )
        db.session.add(progress)

    if user_input == correct_answer:
        progress.solved = True
        progress.solved_at = datetime.utcnow()
        db.session.commit()
        flash('✅ Правильно!','success')
    else:
        flash('❌ Неверно, попробуйте снова','error_timed')

    return redirect(url_for('main_index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if User.query.filter_by(username=username).first():
            flash('Имя пользователя уже занято')
            return redirect(url_for('register'))

        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        return redirect(url_for('main_index'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if not user or not user.check_password(password):
            flash('Неверное имя пользователя или пароль')
            return redirect(url_for('login'))

        login_user(user)
        return redirect(url_for('main_index'))

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main_index'))

