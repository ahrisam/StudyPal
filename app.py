from flask import Flask, request, render_template, url_for, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, login_user, logout_user, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
# from itsdangerous import URLSafeSerializer
from dotenv import load_dotenv
from flask_dance.contrib.google import make_google_blueprint, google
import os

#Initialising the Flask app
app = Flask(__name__)

#Configurations
load_dotenv()
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URI")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]= False
app.config["GOOGLE_CLIENT_SECRET"] = os.getenv("GOOGLE_CLIENT_SECRET")
app.config["Google_CLIENT_ID"] = os.getenv("Google_CLIENT_ID")
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

#Initialising extentions
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
db = SQLAlchemy(app)

#Setting Up google OAuth
google_bp = make_google_blueprint(
    client_id = os.getenv("Google_CLIENT_ID"),
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET"),
    redirect_to = "google_login",
    scope = ["profile","email"]
)
app.register_blueprint(google_bp, url_prefix = "/login")

#Setting up the Database; using SQLAlchemy and Flask-Login intergration
class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique = True)
    password = db.Column(db.String(200), nullable = False)

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password

#DB for user profile
class Profile(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    fname = db.Column(db.String(100))
    avatar = db.Column(db.String(255))
    age = db.Column(db.String(40))


    def __init__(self, fname, age, avatar):
        self.fname = fname
        self.age = age
        self.avatar = avatar

#Welcome page/landing page
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        return redirect(url_for("login"))
    return render_template("landing.html")

#Load user function required by flask
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("nm")
        password = request.form.get("password")

        user_data = User.query.filter_by(name=username).first()
        if user_data and check_password_hash(user_data.password, password):
            login_user(user_data)
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid username or password.")
    return render_template("login.html")


#Google login
@app.route("/login/google/authorized")
def google_login():
    if not google.authorized:
        return redirect(url_for("google.login"))
    response = google.get("/oauth2/v2/userinfo")
    if response.ok:
        user_info = response.json()
        return f"hello, {user_info["name"]}"

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", name = current_user.name)
    
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
        login_user(new_user)

        flash("Account created successfully")
        session["user"] = name
        return redirect(url_for("profile_set"))
    
    return render_template("signup.html")

@app.route("/profile-setup", methods=["POST","GET"])
def profile_set():
    if request.method == "POST":
        fullname = request.form["fullname"]
        age = request.form["age"]
        avatar = request.form["avatar"]

        existing_profile = Profile.query.filter_by(fname = fullname).first()
        if existing_profile:
            return redirect(url_for("dashboard"))
        
        new_profile = Profile(fullname, age)
        db.session.add(new_profile)
        db.session.commit()
        return redirect(url_for("dashboard"))
    return render_template("profileset.html")

@app.route("/logout")
@login_required
def logout():
    login_user()
    return redirect(url_for("login"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)