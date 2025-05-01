from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from models import CodeStatus, CORRECT_ANSWERS

app = Flask(__name__)
app.secret_key = '8b9f28a56878e86e8eef3296ff8b050e2a23e2941bd555cc'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///codes.db'
db = SQLAlchemy(app)


with app.app_context():
    db.create_all()
    if CodeStatus.query.count() == 0:
        for i in range(1, 18):
            db.session.add(CodeStatus(number=i))
        db.session.commit()


@app.route('/')
def index():
    codes = CodeStatus.query.order_by(CodeStatus.number).all()
    return render_template('index.html', codes=codes, CORRECT_ANSWERS=CORRECT_ANSWERS)


@app.route('/check/<int:code_id>', methods=['POST'])
def check(code_id):
    code = CodeStatus.query.get_or_404(code_id)
    user_input = request.form['morse'].strip()

    if user_input == CORRECT_ANSWERS.get(code.number, ""):
        code.solved = True
        db.session.commit()
        flash('✅ Правильно!', 'success')
    else:
        flash('❌ Неверно, попробуй снова', 'error')

    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)