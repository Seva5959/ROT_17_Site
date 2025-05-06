from flask import Flask, render_template, request, redirect, url_for, flash, abort, jsonify
from models import CodeStatus, CORRECT_ANSWERS, db, UserProgress, User, CodeAttempt, AdminMessage, Message
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
    progress = UserProgress.query.filter_by(user_id=current_user.id).all()
    codes = CodeStatus.query.all()
    solved_dict = {p.code_id: p.solved for p in progress}

    for code in codes:
        code.solved = solved_dict.get(code.id, False)
        code.roman_number = to_roman(code.number)

    all_solved = all(code.solved for code in codes)
    full_link = ""

    if all_solved:
        for i in range(1, 18):
            full_link += CORRECT_ANSWERS.get(i, "")

    return render_template('index.html',
                           codes=codes,
                           answers=CORRECT_ANSWERS,
                           all_solved=all_solved,
                           full_link=full_link)


@app.route('/check/<int:code_id>', methods=['POST'])
@login_required
def check(code_id):
    user_input = request.form['decoded_text'].strip()
    code = CodeStatus.query.get(code_id)
    if not code:
        flash('❌ Код не найден')
        return redirect(url_for('main_index'))

    correct_answer = CORRECT_ANSWERS.get(code.number)
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
        flash('✅ Правильно!', 'success')
    else:
        db.session.commit()
        flash('❌ Неверно, попробуйте снова', 'error_timed')

        if check_consecutive_failures(code_id):
            flash('show_hint|' + str(code_id), 'hint')

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


# Админские маршруты
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        abort(403)

    # Все пользователи
    users = User.query.all()

    # Подсчет всех непрочитанных сообщений для всех администраторов
    unread_count = AdminMessage.query.filter_by(read=False).count()

    # Подсчет всех непрочитанных сообщений для текущего администратора
    # Если вы хотите показывать только те сообщения, которые были отправлены конкретному администратору
    user_messages_count = Message.query.filter_by(read=False).count()

    # Подсчет сообщений, отправленных конкретному администратору
    admin_messages_count = AdminMessage.query.filter_by(admin_id=current_user.id, read=False).count()

    return render_template('admin/dashboard.html',
                           users=users,
                           unread_count=unread_count,
                           user_messages_count=user_messages_count,
                           admin_messages_count=admin_messages_count)


@app.route('/admin/user/<int:user_id>')
@login_required
def user_details(user_id):
    if not current_user.is_admin:
        abort(403)

    user = User.query.get_or_404(user_id)
    progress = UserProgress.query.filter_by(user_id=user_id).all()
    successful_attempts = CodeAttempt.query.filter_by(
        user_id=user_id,
        is_correct=True
    ).order_by(desc(CodeAttempt.attempt_time)).all()

    unsuccessful_attempts = CodeAttempt.query.filter_by(
        user_id=user_id,
        is_correct=False
    ).order_by(desc(CodeAttempt.attempt_time)).all()

    codes = CodeStatus.query.all()
    progress_dict = {p.code_id: p for p in progress}

    return render_template('admin/user_details.html',
                           user=user,
                           codes=codes,
                           progress_dict=progress_dict,
                           successful_attempts=successful_attempts,
                           unsuccessful_attempts=unsuccessful_attempts,
                           CORRECT_ANSWERS=CORRECT_ANSWERS)


# Система сообщений
@app.route('/user/messages')
@login_required
def user_messages():
    messages = AdminMessage.query.filter_by(user_id=current_user.id).order_by(AdminMessage.created_at.desc()).all()
    return render_template('user_messages.html', messages=messages)


@app.route('/user/messages/<int:message_id>')
@login_required
def view_user_message(message_id):
    message = AdminMessage.query.get_or_404(message_id)

    if message.user_id != current_user.id:
        flash('Доступ запрещен', 'error')
        return redirect(url_for('user_messages'))

    if not message.read:
        message.read = True
        message.read_at = datetime.utcnow()
        db.session.commit()

    return render_template('user_message_details.html', message=message)


@app.route('/user/reply/<int:message_id>', methods=['GET', 'POST'])
@login_required
def reply_to_admin(message_id):
    # Получаем сообщение от администратора
    admin_message = AdminMessage.query.get_or_404(message_id)

    # Проверяем, что пользователь, который пытается ответить, является владельцем сообщения
    if admin_message.user_id != current_user.id:
        flash('Доступ запрещен', 'error')
        return redirect(url_for('user_messages'))

    # Проверяем, был ли уже отправлен ответ на это сообщение
    existing_reply = Message.query.filter_by(reply_to=message_id).first()
    if existing_reply:
        flash('Вы уже отправили ответ на это сообщение', 'error')
        return redirect(url_for('user_messages'))

    # Обрабатываем форму ответа
    if request.method == 'POST':
        message_text = request.form.get('message')

        # Проверка на пустое сообщение
        if not message_text or len(message_text.strip()) == 0:
            flash('Сообщение не может быть пустым', 'error')
            return redirect(url_for('reply_to_admin', message_id=message_id))

        # Создаем новый ответ
        message = Message(
            user_id=current_user.id,
            admin_id=admin_message.admin_id,
            code_id=admin_message.code_id,
            message=message_text,
            created_at=datetime.utcnow(),
            read=False,
            reply_to=message_id
        )

        # Добавляем ответ в базу данных
        db.session.add(message)
        db.session.commit()

        flash('Ваш ответ отправлен администратору', 'success')
        return redirect(url_for('user_messages'))

    # Отображаем страницу для отправки ответа
    return render_template('reply_to_admin.html', message=admin_message)


@app.route('/admin/send_message/<int:user_id>', methods=['GET', 'POST'])
@login_required
def send_message_to_user(user_id):
    if not current_user.is_admin:
        flash('Доступ запрещен', 'error')
        return redirect(url_for('main_index'))

    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        message_text = request.form.get('message')

        if not message_text or len(message_text.strip()) == 0:
            flash('Сообщение не может быть пустым', 'error')
            return redirect(url_for('send_message_to_user', user_id=user_id))

        admin_message = AdminMessage(
            user_id=user.id,
            message=message_text,
            created_at=datetime.utcnow(),
            read=False
        )

        db.session.add(admin_message)
        db.session.commit()

        flash(f'Сообщение отправлено пользователю {user.username}', 'success')
        return redirect(url_for('admin_messages'))

    return render_template('admin/send_message.html', user=user)


@app.route('/admin/messages')
@login_required
def admin_messages():
    if not current_user.is_admin:
        abort(403)

    messages = AdminMessage.query.order_by(AdminMessage.created_at.desc()).all()
    return render_template('admin/messages.html', messages=messages)


@app.route('/admin/messages/<int:message_id>', methods=['GET', 'POST'])
@login_required
def view_message(message_id):
    if not current_user.is_admin:
        abort(403)

    message = AdminMessage.query.get_or_404(message_id)

    if not message.read:
        message.read = True
        message.read_at = datetime.utcnow()
        db.session.commit()

    if request.method == 'POST':
        reply_text = request.form.get('message')
        if not reply_text or len(reply_text.strip()) == 0:
            flash('Сообщение не может быть пустым', 'error')
        else:
            reply = AdminMessage(
                user_id=message.user_id,
                admin_id=current_user.id,
                code_id=message.code_id,
                message=reply_text.strip(),
                created_at=datetime.utcnow(),
                read=False
            )
            db.session.add(reply)
            db.session.commit()
            flash('Ответ отправлен пользователю', 'success')
            return redirect(url_for('admin_messages'))

    return render_template('admin/message_details.html', message=message)

# Вспомогательные функции
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


def check_consecutive_failures(code_id):
    recent_attempts = CodeAttempt.query.filter_by(
        user_id=current_user.id,
        code_id=code_id,
        is_correct=False
    ).order_by(desc(CodeAttempt.attempt_time)).limit(3).all()

    if len(recent_attempts) < 3:
        return False

    last_success = CodeAttempt.query.filter_by(
        user_id=current_user.id,
        code_id=code_id,
        is_correct=True
    ).order_by(desc(CodeAttempt.attempt_time)).first()

    if not last_success or last_success.attempt_time < recent_attempts[-1].attempt_time:
        return True

    return False


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


@app.route('/send_message_to_admin', methods=['POST'])
@login_required
def send_message_to_admin():
    code_id = request.form.get('code_id')
    message_text = request.form.get('message')

    # Проверка на пустое сообщение
    if not message_text or message_text.strip() == "":
        return jsonify({'success': False, 'error': 'Пустое сообщение'}), 400

    try:
        # Преобразование code_id в int (если это нужно)
        code_id = int(code_id) if code_id else None

        # Создание нового сообщения
        admin_message = AdminMessage(
            user_id=current_user.id,
            message=message_text.strip(),
            code_id=code_id,
            created_at=datetime.utcnow(),
            read=False
        )

        db.session.add(admin_message)
        db.session.commit()

        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500