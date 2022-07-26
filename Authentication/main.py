from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

app = Flask(__name__)

app.config['SECRET_KEY'] = 'any-secret-key-you-choose'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

loginManager = LoginManager()
loginManager.init_app(app)


# CREATE TABLE IN DB
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))


# Line below only required once, when creating DB.
# db.create_all()


@loginManager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        hashed_and_salted_password = generate_password_hash(
            password=request.form.get('password'),
            method='pbkdf2:sha256',
            salt_length=8
        )
        entered_email = request.form.get('email')
        email_exists = User.query.filter_by(email=entered_email).first()
        if email_exists:
            flash('Email already exists.')
            return redirect(url_for('login'))
        else:
            new_user = User(
                email=entered_email,
                password=hashed_and_salted_password,
                name=request.form.get('name')
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('secrets', name=new_user.name))
    return render_template("register.html")


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if not user:
            flash('Email does not exist')
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, password):
            flash('Password is not correct')
            return redirect(url_for('login'))
        else:
            login_user(user)
            flash('Logged in Successfully.')
            return redirect(url_for('secrets'))

    return render_template("login.html")


@app.route('/secrets')
@login_required
def secrets():
    return render_template("secrets.html", name=current_user.name)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/download')
@login_required
def download():
    return send_from_directory('static', 'files/cheat_sheet.pdf')


if __name__ == "__main__":
    app.run(debug=True)