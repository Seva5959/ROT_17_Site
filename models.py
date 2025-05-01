from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()
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

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    password_hash = db.Column(db.String(128))

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




