from app_1 import db

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

class CodeStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, unique=True)
    solved = db.Column(db.Boolean, default=False)




