from flask import Flask, request, render_template, url_for, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "hello"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]= False

db = SQLAlchemy(app)

class users(db.Model):
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
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["nm"]
        password = request.form["password"]

        user_data = users.query.filter_by(name=username).first()
        if user_data and check_password_hash(user_data.password, password):
            session["user"] = user_data.name
            return redirect(url_for('user'))
        else:
            return "Invalid username or password."

    return render_template("login.html")

@app.route("/user")
def user():
    if "user" in session:
        user = session["user"]
        return f"<h1>{user}</h1>"
    else:
        if "user" in session:
            return redirect(url_for("user"))
        return redirect(url_for("login"))

@app.route("/signup", methods=["GET","POST"])
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password_raw = request.form["password"]

        existing_user = users.query.filter_by(email=email).first()
        if existing_user:
            return flash("Account exist already")

        password_hashed = generate_password_hash(password_raw)
        new_user = users(name, email, password_hashed)
        db.session.add(new_user)
        db.session.commit()

        return flash("Account created! You can now log in.")
    
    return render_template("signup.html")
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
