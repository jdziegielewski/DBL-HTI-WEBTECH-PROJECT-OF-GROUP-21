import os, shutil
from flask import Flask, render_template, request, redirect, flash

ALLOWED_EXTENSIONS = ["csv"]

app = Flask(__name__)
app.secret_key = "random string"

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

target = os.path.join(APP_ROOT, "uploaded files")
if os.path.isdir(target):
    shutil.rmtree(target)
os.mkdir(target)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def main_page():
    return render_template("upload.html")

@app.route("/upload", methods = ["POST", "GET"])
def upload_file():
    if request.method == "POST":
        if "file" not in request.files:
            flash("No file selected", "error")
            return redirect("/")

        file = request.files["file"]

        if file.filename == "":
            flash("No file selected", "error")
            return redirect("/")

        if not allowed_file(file.filename):
            flash("File has wrong extension, please upload a .csv file", "error")
            return redirect("/")

        destination = "/".join([target, file.filename])
        file.save(destination)
        flash("File successfully uploaded!", "success")
        return redirect("/")

    else:
        return redirect("/")

if __name__ == "__main__":
    app.run(debug = True)
