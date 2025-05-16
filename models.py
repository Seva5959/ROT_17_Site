from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class UserProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    code_id = db.Column(db.Integer, db.ForeignKey('code_status.id'))
    solved = db.Column(db.Boolean, default=False)
    solved_at = db.Column(db.DateTime)



class CodeStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, unique=True)
    solved = db.Column(db.Boolean, default=False)


class CodeAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    code_id = db.Column(db.Integer, db.ForeignKey('code_status.id'))
    input_text = db.Column(db.String(200))  # Введённый пользователем текст
    is_correct = db.Column(db.Boolean, default=False)  # Верна ли попытка
    attempt_time = db.Column(db.DateTime)  # Время попытки

    # Добавим связи для удобства в запросах
    user = db.relationship('User', backref=db.backref('attempts', lazy=True))
    code = db.relationship('CodeStatus', backref=db.backref('attempts', lazy=True))


class AdminMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # ➕ Добавлено
    message = db.Column(db.Text)
    code_id = db.Column(db.Integer, db.ForeignKey('code_status.id'))
    created_at = db.Column(db.DateTime)
    read = db.Column(db.Boolean, default=False)

    user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('admin_messages', lazy=True))
    admin = db.relationship('User', foreign_keys=[admin_id])  # ➕ Добавлено
    code = db.relationship('CodeStatus', backref=db.backref('messages', lazy=True))

    read_by_user = db.Column(db.Boolean, default=False)
    read_by_admin = db.Column(db.Boolean, default=False)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    code_id = db.Column(db.Integer, db.ForeignKey('code_status.id'))
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    read_by_user = db.Column(db.Boolean, default=False)
    read_by_admin = db.Column(db.Boolean, default=False)

    reply_to = db.Column(db.Integer, db.ForeignKey('message.id'))  # ID родительского сообщения, если это ответ
    read_at = db.Column(db.DateTime)

    # Связи
    user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('messages', lazy=True))
    admin = db.relationship('User', foreign_keys=[admin_id],
                            backref=db.backref('admin_responses', lazy=True))  # Изменили имя
    code = db.relationship('CodeStatus', backref=db.backref('code_messages', lazy=True))  # Изменили на 'code_messages'
    reply = db.relationship('Message', remote_side=[id],
                            backref=db.backref('replies', lazy='dynamic'))  # Ответы на сообщение

CORRECT_ANSWERS = {
    1: "https:/",
    2: "/docs.",
    3: "google.",
    4: "com/doc",
    5: "ument/d/",
    6: "1gG4e",
    7: "Xhu9",
    8: "-l3V",
    9: "hYGGS",
    10: "wP0a",
    11: "VoDuih",
    12: "ju2Snf",
    13: "1XDQ5",
    14: "rQcwc/",
    15: "edit?usp",
    16: "=sharing",
    17: "6209"
}
