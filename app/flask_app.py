import os, shutil, cloudpickle
import xlrd, json
import numpy as np
import time
# import visualization
import pandas as pd
import networkx as nx
from bokeh.embed import components
from bokeh.client import pull_session
from bokeh.embed import server_session
from flask import Flask, render_template, session, request, redirect, flash, send_file

app = Flask(__name__)
app.secret_key = b'|\xeb \xccP6\xbe\x9c0\x86\xa55\x8dz\x9f\x95'

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = ["csv", "txt", "xlsx", "xls", "xlsm", "json", "zip", "gz", "xz", "bz2"]

LAST_FILE = ""


#For saving SEPARATORS
def save_obj(obj, name):
    with open('uploads/'+ name + '.pkl', 'wb') as file:
        cloudpickle.dump(obj, file)


def load_obj(name):
    with open('uploads/' + name + '.pkl', 'rb') as file:
        return cloudpickle.load(file)


@app.route('/')
def index():
    return render_template("index.html", last_file=get_last_file())


@app.route('/thesis')
def index1():
    return render_template("index-thesis.html", last_file=get_last_file())


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


def load_local(filename, sep=';'):
    path = os.path.join(UPLOAD_FOLDER, filename)
    dataframe = pd.read_csv(path, sep=sep, index_col=0)
    dataframe = dataframe.stack().reset_index()
    dataframe = dataframe[dataframe[0] > 0]
    dataframe.columns = ['start', 'end', 'weight']
    #dg = nx.from_pandas_adjacency(dataframe)
    return dataframe
    #load_obj(filename) # <- this function replaces this ^ function


def store_local_adm(filename, sep=None, edgelist=False):
    #---------------------------------
    path = os.path.join('temp', filename)
    if sep == "excel":
        dataframe = pd.read_excel(path, engine='xlrd', index_col=0)
    elif sep == "json":
        #dataframe = pd.read_json(path) #read_json doesn't cooperate with the json I have
        with open(path) as jsn:
            jsn_dict = json.load(jsn)
        preserved_order = []
        for people in jsn_dict:
            preserved_order.append(people)
        dataframe = pd.DataFrame.from_dict(jsn_dict, orient='index')
        dataframe = dataframe.reindex(preserved_order)
    else:
        if sep != "":
            dataframe = pd.read_csv(path, sep=sep, engine="c", index_col=0)
        else:
            dataframe = pd.read_csv(path, sep=None, engine="python", index_col=0)#python engine can infer separators to an extent
    
    if 'Unnamed: 0' in dataframe.columns.values:
        dataframe.columns = np.append(np.delete(dataframe.columns.values, 0), 'NaNs')#dealing with end of line separators (malformed csv/txt)
        dataframe = dataframe.drop('NaNs', axis=1)
    if not edgelist:
        print(dataframe)
        if adm_check(dataframe):
            return dataframe
        else:
            flash("Uploaded dataset does not have adjacency matrix format. Did you mean to upload an edge list?", "error")
            return redirect('/files')
    else:
        dataframe['edge_idx'] = dataframe.index
        dataframe.columns = ['start', 'end', 'weight', 'edge_idx']
        if edli_check(dataframe):
            dataframe = edli2adm(dataframe)
            return dataframe
        else:
            flash(flash("Uploaded dataset does not have edge list format. Did you mean to upload an adjacency matrix?", "error"))


def adm_check(dataframe):
    if dataframe.shape != (len(dataframe), len(dataframe)): #if not nxn matrix (wrong format) return False
        return False
    return True
    #----------------------------------


def edli_check(dataframe):
    if dataframe.shape != (len(dataframe), 4): #if not nx4 edge list (wrong format) return False
        return False
    return True


def edli2adm(dataframe):
    nodes = dataframe.start.unique()
    np.append(nodes, dataframe.end.unique())
    nodes = list(dict.fromkeys(nodes))
    adm = pd.DataFrame(index=nodes, columns=nodes)
    for i in range(len(dataframe['start'])):
        adm[dataframe['start'][i]][dataframe['end'][i]] = dataframe['weight'][i]
        adm = adm.fillna(0)
    return adm


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
            flash("File has wrong extension, please upload a supported filetype", "error")
            return redirect("/files")
    # v preprocess? v
        target = os.path.join(APP_ROOT, 'temp')
        if not os.path.isdir(target):
            os.mkdir(target)

        destination = "/".join([target, file.filename])
        file.save(destination)
    
        if file.filename.rsplit(".", 1)[1].lower() in ["xlsx", "xls", "xlsm"]:
            SEPARATOR = "excel"
        elif file.filename.rsplit(".", 1)[1].lower() == "json":
            SEPARATOR = "json"
        else:
            SEPARATOR = request.form["sep"]
        df = store_local_adm(file.filename, sep=SEPARATOR, edgelist=request.form.get("edgelist"))
        if isinstance(df, pd.DataFrame):
            save_obj(df, file.filename)
            os.remove(os.path.join("temp", file.filename))
            flash("File successfully uploaded!", "success")
        return redirect("/files")
    else:
        if os.path.isdir('temp'):
            shutil.rmtree('temp')
        os.mkdir('temp')
        target = os.path.join(APP_ROOT, UPLOAD_FOLDER)
        uploaded_files = os.listdir(target)
        for i in range(len(uploaded_files)):
            uploaded_files[i] = uploaded_files[i].replace('.pkl', '')
        return render_template("files.html", files=uploaded_files, last_file=get_last_file())
    # ^             ^


@app.route('/download')
def download():
    filename = request.args.get("file")
    df = load_obj(filename)
    download = df.to_csv()
    filepath = os.path.join("temp", filename+".csv")
    with open(filepath, 'w') as file:
        file.write(download)
    return send_file(filepath, attachment_filename=filename + ".csv", as_attachment=True, mimetype='text/csv')


@app.route('/documentation')
def documentation():
    return render_template('documentation.html', section=request.args.get('section'), last_file=get_last_file())


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