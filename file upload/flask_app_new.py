import os, shutil
from flask import Flask, render_template, request, redirect, flash

ALLOWED_EXTENSIONS = ["csv"]

app = Flask(__name__)
app.secret_key = "random string"

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

if os.path.isdir('/upload'):
    shutil.rmtree('/upload')
    os.mkdir('/upload') #When script is closed, upload directory will be still intact on next launch. This clears the directory.

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def main_page():
    uploaded_files = os.listdir('/upload') #Added files argument for displaying uploaded files
    return render_template("upload_new.html", files=uploaded_files)

@app.route("/upload", methods = ["POST", "GET"])
def upload_file():
    if request.method == 'POST':
        if "file" not in request.files:
            flash("No file selected", "error")
            return redirect("/")

        file = request.files["file"]

        if not allowed_file(file.filename):
            flash("File has wrong extension, please upload a .csv file", "error")
            return redirect("/")

        destination = "/".join(['/upload', file.filename]) #Changed name from always being upload.csv to file.filename
        file.save(destination)
        flash("File successfully uploaded!", "success")
        return redirect("/")

    else:
        return redirect("/")

if __name__ == "__main__":
    app.run(debug = True)
