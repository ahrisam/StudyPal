from flask import Flask, request, render_template, url_for, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeSerializer
from dotenv import load_dotenv
import os

app = Flask(__name__)
load_dotenv()
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]= False

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = "users"
    _id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column("name", db.String(100))
    email = db.Column("email", db.String(100))
    password = db.Column("password", db.String(200))

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        return redirect(url_for("login"))
    return render_template("landing.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("nm")
        password = request.form.get("password")

        user_data = User.query.filter_by(name=username).first()
        if user_data and check_password_hash(user_data.password, password):
            session["user"] = user_data.name
            return redirect(url_for('user'))
        else:
            flash("Invalid username or password.")

    return render_template("login.html")

@app.route("/dashboard")
def user():
    if "user" in session:
        user = session["user"]
        return f"<h1>Welcome {user}</h1>"
    else:
        if "user" in session:
            return redirect(url_for("user"))
        return redirect(url_for("login"))

@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method == "POST":
        name = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Account exist already")
            return redirect(url_for('login'))

        password_hashed = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
        new_user = User(name, email, password_hashed)
        db.session.add(new_user)
        db.session.commit()

        flash("Account created successfully")
        session["user"] = name
        return redirect(url_for("user"))
    
    return render_template("signup.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
