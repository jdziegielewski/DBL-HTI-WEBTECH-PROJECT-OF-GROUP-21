import os
import numpy as np
import visualization
import pandas as pd
import networkx as nx
from bokeh.embed import components
from bokeh.client import pull_session
from bokeh.embed import server_session
from flask import Flask, render_template, session, request, redirect, flash

app = Flask(__name__)
app.secret_key = b'|\xeb \xccP6\xbe\x9c0\x86\xa55\x8dz\x9f\x95'

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = ["csv"]

LAST_FILE = ""

@app.route('/')
def index():
    return render_template("index.html", last_file=get_last_file())


@app.route('/visualization')
def redirect_to_files():
    with pull_session(url="http://localhost:5006/") as s:
        script = server_session(session_id=s.id, url='http://localhost:5006/')
    return render_template("visualization.html", script=script, last_file=get_last_file())
    #if 'last_file' in session:
        #return redirect('/visualization/' + session['last_file'])
    #return redirect('/files')


@app.route('/visualization/<filename>')
def visualize_file(filename):
    session['last_file'] = filename
    graph = load_local(filename)
    dashboard = visualization.create_dashboard(graph, filename)
    script, div = components(dashboard)
    return render_template("visualization.html", script=script, div=div, last_file=get_last_file())

@app.route('/close')
def close_file():
    session.clear()
    return redirect('/files')


def load_local(filename, sep=';', clean=True):
    path = os.path.join(UPLOAD_FOLDER, filename)
    df = pd.read_csv(path, sep=sep, index_col=0)
    df = df.stack().reset_index()
    df = df[df[0] > 0]
    df.columns = ['start', 'end', 'weight']
    #dg = nx.from_pandas_adjacency(df)
    return df


@app.route("/files", methods=["POST", "GET"])
def files():
    if request.method == 'POST':
        if "file" not in request.files:
            flash("No file selected", "error")
            return redirect("/files")

        file = request.files["file"]

        if file.filename == "":
            flash("No file selected", "error")
            return redirect("/files")
        
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
        return render_template("files.html", files=uploaded_files, last_file=get_last_file())


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def get_last_file():
    return retrieve_or_default(session, 'last_file', 'Visualization')


def retrieve_or_default(dict, key, default):
    if key in dict:
        return dict[key]
    return default


if __name__ == '__main__':
    app.run(port=5000, debug=True)