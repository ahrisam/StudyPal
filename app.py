from flask import Flask, request, render_template

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def start():
    if request.method == "POST":
        return "<h2>hello</h2>"
    return render_template("landing.html")

if __name__ == "__main__":
    app.run(debug=True)