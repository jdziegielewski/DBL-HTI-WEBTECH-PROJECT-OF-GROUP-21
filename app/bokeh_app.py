import os
import sidebar
import cloudpickle
import numpy as np
import holoviews as hv
from bokeh.server.server import Server
from tornado.ioloop import IOLoop
from nodelink import NodeLink
from admatrix import AdMatrix

# renderer = hv.renderer('bokeh').instance(mode='server', webgl=True)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = "uploads"

def load_local(name):
    with open('uploads/' + name + '.pkl', 'rb') as file:
        return cloudpickle.load(file)


def get_edge_list(df):
    edge_list = df.stack().reset_index()
    edge_list = edge_list[edge_list[0] > 0]
    edge_list.columns = ['start', 'end', 'weight']
    edge_list = edge_list.reset_index()
    edge_list['edge_idx'] = edge_list.index
    return edge_list


def add_missing_nodes(df, edge_list):
    index_edge_list = np.unique(edge_list[["start", "end"]].values)
    index_dataframe = df.index
    if len(index_edge_list) != len(index_dataframe):
        diff = set(index_dataframe) - set(index_edge_list)
        for i in diff:
            edge_list = edge_list.append({"start": i, "end": i, "weight": 0}, ignore_index=True)
    return edge_list


def modify_doc(doc):
    args = doc.session_context.request.arguments
    filename = str(args['filename'][0].decode('utf-8'))
    filename = os.path.join(APP_ROOT, UPLOAD_FOLDER, filename)
    df = load_local(filename)
    edges = get_edge_list(df)
    nodelink = NodeLink(hv.Table(add_missing_nodes(df, edges)))
    admatrix = AdMatrix(hv.Table(edges), df)
    nodelink.link_admatrix(admatrix)
    admatrix.link_nodelink(nodelink)
    return sidebar.create(nodelink.param, nodelink.view, admatrix.param, admatrix.view).server_doc(doc=doc)


def io_worker():
    server = Server({'/bokeh_app': modify_doc}, io_loop=IOLoop(), allow_websocket_origin=["*"])
    server.start()
    server.io_loop.start()
    return
