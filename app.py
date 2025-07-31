from flask import Flask, request, render_template, url_for, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeSerializer
from dotenv import load_dotenv
from flask_dance.contrib.google import make_google_blueprint, google
import os

app = Flask(__name__)
load_dotenv()
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URI")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]= False
app.config["GOOGLE_CLIENT_SECRET"] = os.getenv("GOOGLE_CLIENT_SECRET")
app.config["Google_CLIENT_ID"] = os.getenv("Google_CLIENT_ID")
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


db = SQLAlchemy(app)
google_bp = make_google_blueprint(
    client_id = os.getenv("Google_CLIENT_ID"),
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET"),
    redirect_to = "google_login",
    scope = ["profile","email"]
)
app.register_blueprint(google_bp, url_prefix = "/login")

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

class Profile(db.Model):
    _id = db.Column(db.Integer, primary_key = True)
    avatar = db.Column(db.String(100))
    gender = db.Column(db.String(10))
    isActive = db.Column(db.Boolean())

    def __init__(self, avatar, gender, isActive):
        self.avatar = avatar
        self.gender = gender
        self.isActive = isActive

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

@login_manager.user_loader
def load_user():
    return User.query.get(int(id))

@app.route("/login/google/authorized")
def google_login():
    if not google.authorized:
        return redirect(url_for("google.login"))
    response = google.get("/oauth2/v2/userinfo")
    if response.ok:
        user_info = response.json()
        return f"hello, {user_info["name"]}"

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
        return redirect(url_for("profile_set"))
    
    return render_template("signup.html")

@app.route("/profile-setup")
@login_required
def profile_set():
    return render_template("profileset.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)