from flask import Flask, request, render_template, url_for, redirect

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def start():
    if request.method == "POST":
        return redirect(url_for("login"))
    return render_template("landing.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form["nm"]
        return redirect(url_for("user", usr=user))
    else:
        return render_template("login.html")

@app.route("/<usr>")
def user(usr):
    return f"<h1>{usr}</h1>"

if __name__ == "__main__":
    app.run(debug=True)