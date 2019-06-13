import sys
import sidebar
import cloudpickle
import holoviews as hv
from nodelink import NodeLink
from admatrix import AdMatrix
from bokeh.server.server import Server

renderer = hv.renderer('bokeh').instance(mode='server', webgl=True)


def load_local(name):
    with open('uploads/' + name + '.pkl', 'rb') as file:
        return cloudpickle.load(file)


def get_edge_list(df):
    edge_list = df.stack().reset_index()
    edge_list = edge_list[edge_list[0] > 0]
    edge_list.columns = ['start', 'end', 'weight']
    edge_list = edge_list.reset_index()
    edge_list['edge_idx'] = edge_list.index
    return hv.Table(edge_list)


filename = sys.argv[1]
df = load_local(filename)
edges = get_edge_list(df)


def modify_doc(doc):
    nodelink = NodeLink(edges)
    admatrix = AdMatrix(edges, df)
    nodelink.link_admatrix(admatrix)
    admatrix.link_nodelink(nodelink)
    return sidebar.create(nodelink.param, nodelink.view, admatrix.param, admatrix.view).server_doc(doc=doc)


server = Server({'/': modify_doc}, port=5006, allow_websocket_origin=['*'])
server.start()
server.run_until_shutdown()
