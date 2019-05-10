import pandas as pd
import os
from flask import Flask, render_template, request
from bokeh.embed import components
import visualization
import networkx as nx
# from bokeh.plotting import curdoc
import os
from bokeh.client import pull_session
from bokeh.embed import server_session
from flask import Flask, render_template, request, redirect, flash

app = Flask(__name__)
app.secret_key = b'|\xeb \xccP6\xbe\x9c0\x86\xa55\x8dz\x9f\x95'

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = ["csv"]

LAST_FILE = ""


@app.route('/')
def index():
    return render_template("index.html", template="Flask")


@app.route('/visualization')
def redirect_to_files():
    #if last_selected_file is not None:
        #return redirect('/visualization/' + last_selected_file)
    return redirect('/files')


@app.route('/visualization/<filename>')
def visualize_file(filename):
    graph = load_local(filename)
    dashboard = visualization.create_dashboard(graph, filename)
    script, div = components(dashboard)
    return render_template("visualization.html", script=script, div=div, template="Flask")


def load_local(filename, sep=';', clean=True):
    path = os.path.join(UPLOAD_FOLDER, filename)
    df = pd.read_csv(path, sep=sep)
    if clean:
        df = df.loc[:, df.columns[1:]]
    dg = nx.DiGraph(df.values)
    return dg


@app.route("/files", methods=["POST", "GET"])
def files():
    if request.method == 'POST':
        if "file" not in request.files:
            flash("No file selected", "error")
            return redirect("/files")

        file = request.files["file"]

        if not allowed_file(file.filename):
            flash("File has wrong extension, please upload a .csv file", "error")
            return redirect("/files")

        target = os.path.join(APP_ROOT, UPLOAD_FOLDER)
        if not os.path.isdir(target):
            os.mkdir(target)

        destination = "/".join([target, file.filename])
        file.save(destination)
        flash("File successfully uploaded!", "success")
        return redirect("/files")

    else:
        target = os.path.join(APP_ROOT, UPLOAD_FOLDER)
        uploaded_files = os.listdir(target)
        return render_template("files.html", files=uploaded_files, template="Flask")


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


if __name__ == '__main__':
    app.run(port=5000, debug=True)
