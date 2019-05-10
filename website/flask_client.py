import os
from bokeh.client import pull_session
from bokeh.embed import server_session
from flask import Flask, render_template, request, redirect, flash

ALLOWED_EXTENSIONS = ["csv"]

app = Flask(__name__)
app.secret_key = "random string"

APP_ROOT = os.path.dirname(os.path.abspath(__file__))


@app.route('/')
def index():
    with pull_session(url="http://localhost:5006/") as session:
        script = server_session(session_id=session.id, url='http://localhost:5006')
    return render_template("index.html", script=script, template="Flask")


@app.route("/upload", methods=["POST", "GET"])
def upload_file():
    #with pull_session(url="http://localhost:5006/") as session:
    #script = server_session(session_id=session.id, url='http://localhost:5006')
    print("UPLOAD LOAD")
    if request.method == 'POST':
        print("UPLOAD START")
        if "file" not in request.files:
            flash("No file selected", "error")
            return redirect("/")

        file = request.files["file"]

        if not allowed_file(file.filename):
            flash("File has wrong extension, please upload a .csv file", "error")
            return redirect("/")

        target = os.path.join(APP_ROOT, "uploaded file")
        if not os.path.isdir(target):
            os.mkdir(target)

        destination = "/".join([target, "upload.csv"])
        file.save(destination)
        flash("File successfully uploaded!", "success")
        print("Upload success")
        return redirect("/")

    else:
        print("UPLOAD LANDING")
        return render_template("website_upload.html", template="Flask")


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


if __name__ == '__main__':
    app.run(port=5000, debug=True)
