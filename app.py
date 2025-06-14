from flask import Flask, request, render_template

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    greeting = ""
    if request.method == "POST":
        name = request.form.get("name", "World")
        greeting = f"Hello {name}"
    return render_template("index.html", greeting=greeting)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
