from flask import Flask, render_template, request, redirect, url_for, flash, abort
from models import CodeStatus, CORRECT_ANSWERS, db, UserProgress, User, CodeAttempt
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime
from sqlalchemy import desc


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
        code.roman_number = to_roman(code.number)

    return render_template('index.html', codes=codes, answers=CORRECT_ANSWERS)


# Изменим функцию проверки, чтобы сохранять попытки
@app.route('/check/<int:code_id>', methods=['POST'])
@login_required
def check(code_id):
    user_input = request.form['decoded_text'].strip()
    # Получаем код по его ID из базы данных
    code = CodeStatus.query.get(code_id)
    if not code:
        flash('❌ Код не найден')
        return redirect(url_for('main_index'))

    correct_answer = CORRECT_ANSWERS.get(code.number)
    progress = UserProgress.query.filter_by(
        user_id=current_user.id,
        code_id=code_id
    ).first()

    # Если прогресс по этому коду ещё не создан — создаём
    if not progress:
        progress = UserProgress(
            user_id=current_user.id,
            code_id=code_id
        )
        db.session.add(progress)

    # Сохраняем попытку в таблицу CodeAttempt
    attempt = CodeAttempt(
        user_id=current_user.id,
        code_id=code_id,
        input_text=user_input,
        is_correct=(user_input == correct_answer),
        attempt_time=datetime.utcnow()
    )
    db.session.add(attempt)

    if user_input == correct_answer:
        progress.solved = True
        progress.solved_at = datetime.utcnow()
        db.session.commit()
        flash('✅ Правильно!','success')
    else:
        db.session.commit()  # Сохраняем даже неверные попытки
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

# Маршрут панели администратора
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        abort(403)  # Запрет, если пользователь не админ

    # Получаем всех пользователей для отображения на панели
    users = User.query.all()
    return render_template('admin/dashboard.html', users=users)

# Маршрут подробностей по пользователю
@app.route('/admin/user/<int:user_id>')
@login_required
def user_details(user_id):
    if not current_user.is_admin:
        abort(403)

    user = User.query.get_or_404(user_id)
    progress = UserProgress.query.filter_by(user_id=user_id).all()

    # Получаем успешные и неуспешные попытки отдельно
    successful_attempts = CodeAttempt.query.filter_by(
        user_id=user_id,
        is_correct=True
    ).order_by(desc(CodeAttempt.attempt_time)).all()

    unsuccessful_attempts = CodeAttempt.query.filter_by(
        user_id=user_id,
        is_correct=False
    ).order_by(desc(CodeAttempt.attempt_time)).all()

    # Получаем все коды (чтобы показать, какие решены, а какие — нет)
    codes = CodeStatus.query.all()

    # Создаём словарь: ID кода → прогресс пользователя
    progress_dict = {p.code_id: p for p in progress}

    return render_template('admin/user_details.html',
                          user=user,
                          codes=codes,
                          progress_dict=progress_dict,
                          successful_attempts=successful_attempts,
                          unsuccessful_attempts=unsuccessful_attempts,
                          CORRECT_ANSWERS=CORRECT_ANSWERS)


@app.route('/admin/remove/<int:user_id>')
@login_required
def remove_admin(user_id):
    if not current_user.is_admin:
        abort(403)

    if user_id == current_user.id:
        flash('Вы не можете удалить свои права администратора')
        return redirect(url_for('admin_dashboard'))

    user = User.query.get_or_404(user_id)
    user.is_admin = False
    db.session.commit()
    flash(f'Пользователь {user.username} больше не администратор')
    return redirect(url_for('admin_dashboard'))

# Сбросить всех админов
@app.route('/admin/reset')
@login_required
def reset_all_admins():
    # Осторожно: сбрасывает права у всех
    User.query.update({User.is_admin: False})
    db.session.commit()
    flash('Все права администраторов сброшены')
    return redirect(url_for('main_index'))


# Маршрут для назначения пользователя администратором
@app.route('/admin/create/<int:user_id>')
@login_required
def make_admin(user_id):
    # Этот маршрут должен быть доступен только один раз — для создания первого админа
    # После этого его нужно ограничить или удалить
    if User.query.filter_by(is_admin=True).count() > 0:
        # Если админ уже существует, то только админ может создать другого админа
        if not current_user.is_admin:
            abort(403)

    user = User.query.get_or_404(user_id)
    user.is_admin = True
    db.session.commit()
    flash(f'Пользователь {user.username} теперь администратор')
    return redirect(url_for('admin_dashboard'))

def to_roman(num):
    val = [
        1000, 900, 500, 400,
        100, 90, 50, 40,
        10, 9, 5, 4, 1
    ]
    syb = [
        "M", "CM", "D", "CD",
        "C", "XC", "L", "XL",
        "X", "IX", "V", "IV", "I"
    ]
    roman_num = ''
    i = 0
    while num > 0:
        for _ in range(num // val[i]):
            roman_num += syb[i]
            num -= val[i]
        i += 1
    return roman_num