import os, cloudpickle
import xlrd, json
import sys
import colorcet
import numpy as np
import panel as pn
import param as pm
import pandas as pd
import networkx as nx
import holoviews as hv
import datashader as ds
from holoviews import opts
from holoviews.streams import Selection1D, Params
from holoviews.element.graphs import layout_nodes
from holoviews.operation.datashader import rasterize, datashade, bundle_graph, dynspread, shade
from bokeh.server.server import Server
from collections import OrderedDict as odict

renderer = hv.renderer('bokeh').instance(mode='server', webgl=True)

def create_node_link_dataset(dataframe):
    # df.values[[np.arange(df.shape[0])] * 2] = 0
    edge_list = dataframe.stack().reset_index()
    edge_list = edge_list[edge_list[0] > 0]
    edge_list.columns = ['start', 'end', 'weight']
    edge_list = edge_list.reset_index()

    index_edge_list = np.unique(edge_list[["start", "end"]].values)
    index_dataframe = dataframe.index
    if len(index_edge_list) != len(index_dataframe):
        diff = set(index_dataframe) - set(index_edge_list)
        for i in diff:
            edge_list = edge_list.append({"start" : i, "end" : i, "weight" : 0}, ignore_index=True)

    edge_list['edge_idx'] = edge_list.index
    dataset = hv.Table(edge_list)
    return dataset

def create_ad_matrix_dataset(dataframe):
    # df.values[[np.arange(df.shape[0])] * 2] = 0
    edge_list = dataframe.stack().reset_index()
    edge_list.columns = ['start', 'end', 'weight']
    edge_list = edge_list.reset_index()

    edge_list['edge_idx'] = edge_list.index
    dataset = hv.Table(edge_list)
    return dataset

#For saving SEPARATORS
def save_obj(obj, name):
    with open('properties/'+ name + '.pkl', 'wb') as file:
        cloudpickle.dump(obj, file)

def load_obj(name):
    with open('properties/' + name + '.pkl', 'rb') as file:
        return cloudpickle.load(file)

SEPARATORS = load_obj("sep")

filename = sys.argv[1]
path = os.path.join("uploads", filename)
#dataframe = pd.read_csv(path, sep=';', index_col=0)
#dataframe = pd.read_csv(path, sep=None engine='python', index_col=0) # supports , ; : in csv and txt
#clean=False
if SEPARATORS.get(filename) == "excel":
    dataframe = pd.read_excel(path, engine='xlrd', index_col=0)
elif SEPARATORS.get(filename) == "json":
    #dataframe = pd.read_json(path) #read_json doesn't cooperate with the json I have
    #print(dataframe, orient='split', lines=True)

    with open(path) as jsn:
        jsn_dict = json.load(jsn)
    preserved_order = []
    for people in jsn_dict:
        preserved_order.append(people)
    dataframe = pd.DataFrame.from_dict(jsn_dict, orient='index')
    dataframe = dataframe.reindex(preserved_order)
else:
    dataframe = pd.read_csv(path, sep=None, engine="python", index_col=0)
#if clean:
#    dataframe = dataframe.loc[:, dataframe.columns[1:]]
if dataframe.shape != (len(dataframe), len(dataframe)):
    os.remove(path)
    print('BAD DATASET')
    dataframe = pd.read_csv('uploads/Test_data.csv', sep=';', index_col=0)#placeholder, just so it doesnt error

node_link_dataset = create_node_link_dataset(dataframe)
ad_matrix_dataset = create_ad_matrix_dataset(dataframe)
tools = ['box_select', 'hover', 'tap']

cmaps = {'Colorcet -- Fire': colorcet.fire,
         'Colorcet -- BMY': colorcet.bmy,
         'Colorcet -- BMW': colorcet.bmy,
         'Colorcet -- BGY': colorcet.bgy,
         'Gradient -- Blue-Magenta-Yellow': ['blue', 'magenta', 'yellow'],
         'Solid -- Yellow': ['yellow'],
         'Solid -- Blue': ['blue'],
         'Solid -- Purple': ['purple'],
         'Solid -- Green': ['green'],
         'Solid -- Red': ['red'],
         'Solid -- White': ['white']}

def disable_logo(plot, element):
    plot.state.toolbar.logo = None

class NodeLink(pm.Parameterized):
    layout_dict = {'Circular': nx.layout.circular_layout,
                   'Fruchterman-Reingold': nx.layout.fruchterman_reingold_layout,
                   'Kamada-Kawai': nx.layout.kamada_kawai_layout,
                   'Spring': nx.layout.spring_layout}
    layout = pm.ObjectSelector(label='Layout', default='Circular', objects=layout_dict.keys())

    edge_col = pm.Selector(label='Edge Color', objects=cmaps, default=['blue', 'magenta', 'yellow'])
    edge_alpha = pm.Integer(label='Edge Alpha', default=200, bounds=(0, 255))

    nsel_col = pm.Selector(label='Node Selection Color', objects=cmaps, default=['green'])
    nsel_alpha = pm.Integer(label='Node Selection Alpha', default=200, bounds=(0, 255))

    esel_col = pm.Selector(label='Edge Selection Color', objects=cmaps, default=['purple'])
    esel_alpha = pm.Integer(label='Edge Selection Alpha', default=200, bounds=(0, 255))

    node_size = pm.Number(label='Node Size', default=5, bounds=(1, 10))
    node_col = pm.Color(label='Node Fill Color', default='#2b9ad0')
    line_col = pm.Color(label='Node Line Color', default='#ffffff')
    node_alpha = pm.Magnitude(label='Node Alpha', default=1)

    bg_col = pm.Color(label='Background Color', default='#ffffff')

    bundle = pm.Boolean(label='Edge Bundling', default=False)

    def __init__(self, data, **params):
        super().__init__(**params)
        self.dataset = data
        self.graph = hv.Graph(node_link_dataset, kdims=['start', 'end'], vdims=['weight', 'edge_idx'])
        self.bundled_graph = None
        self.edges = None
        self.nodes = None
        self.last_layout = None
        self.last_bundle = False
        self.dyn_edges = hv.DynamicMap(self.draw_edges)
        self.dyn_nodes = hv.DynamicMap(self.draw_nodes)
        self.node_stream = Selection1D(source=self.dyn_nodes)
        self.dyn_node_select = hv.DynamicMap(self.draw_node_select, streams=[self.node_stream])
        self.dyn_edge_select = None
        self.admatrix = None

    def link_admatrix(self, admatrix):
        self.admatrix = admatrix

    def update_layout(self):
        new_graph = None
        if self.last_layout is not self.layout:
            self.last_layout = self.layout
            self.graph = layout_nodes(self.graph, layout=self.layout_dict[self.last_layout])
            new_graph = self.graph
        if new_graph or self.last_bundle is not self.bundle:
            self.last_bundle = self.bundle
            if self.bundle:
                self.bundled_graph = bundle_graph(self.graph)
                new_graph = self.bundled_graph
            else:
                new_graph = self.graph
        if new_graph:
            self.edges = new_graph.edgepaths
            if not self.last_bundle:
                self.edges = self.edges.add_dimension('weight', 0, node_link_dataset.dframe(dimensions=['weight'])['weight'],
                                                      vdim=True)
            self.nodes = new_graph.nodes
            self.nodes.opts(opts.Nodes(tools=tools))

    def get_graph(self):
        return self.bundled_graph if self.bundle else self.graph

    @pn.depends('layout', 'edge_col', 'bundle')
    def draw_edges(self):
        self.update_layout()
        return self.edges

    @pn.depends('layout', 'node_col', 'line_col', 'node_size', 'node_alpha')
    def draw_nodes(self):
        self.nodes.opts(opts.Nodes(
            color=self.node_col,
            line_color=self.line_col,
            size=self.node_size,
            alpha=self.node_alpha))
        return self.nodes

    @pn.depends('layout', 'bundle')
    def draw_node_select(self, index):
        starts = self.get_graph().nodes.dimension_values('index')[index]
        if len(starts) == 0:
            return hv.Curve(([0], [0]))
        else:
            return self.get_graph().select(start=starts.tolist())

    @pn.depends('layout', 'bundle')
    def draw_edge_select(self, index=None):
        if not index:
            return hv.Curve(([0], [0]))
        else:
            return self.get_graph().select(edge_idx=index)

    def start(self):
        dyn_edges = datashade(self.dyn_edges, cmap=self.param.edge_col, alpha=self.param.edge_alpha)
        self.dyn_edge_select = hv.DynamicMap(self.draw_edge_select, streams=[self.admatrix.edge_stream])
        hv_plot = \
            dyn_edges \
            .opts(xaxis=None, yaxis=None, toolbar='above', responsive=True, aspect=1, finalize_hooks=[disable_logo]) \
            * self.dyn_nodes \
            * dynspread(datashade(self.dyn_node_select, cmap=self.param.nsel_col, alpha=self.param.nsel_alpha), max_px=100) \
            * dynspread(datashade(self.dyn_edge_select, cmap=self.param.esel_col, alpha=self.param.esel_alpha), max_px=100)
        #hv_plot.opts(bgcolor=self.param.bg_col)
        return hv_plot

class AdMatrix(pm.Parameterized):
    markers = {'Square': 's',
               'Circle': 'o',
               'Cross': '+'}
    edge_col = pm.Selector(label='Color', objects=cmaps, default=['blue', 'magenta', 'yellow'])
    marker = pm.Selector(label='Symbol', objects=markers, default='s')
    alpha = pm.Magnitude(label='Alpha', default=0.7)
    nons_alpha = pm.Magnitude(label='Nonselection Alpha', default=0.1)
    size = pm.Number(label='Size', default=5, bounds=(1, 10))
    esel_col = pm.Selector(label='Node Selection Color', objects=cmaps, default=['green'])
    esel_alpha = pm.Magnitude(label='Node Selection Alpha', default=0.7)

    def __init__(self, data, **params):
        super().__init__(**params)
        self.dataset = data
        self.matrix = hv.Points(ad_matrix_dataset, kdims=['start', 'end'], vdims=['weight'])
        self.matrix.opts(opts.Points(tools=tools, toolbar='above'))
        self.matrix.opts(xrotation=90, xaxis='top', labelled=[], color='weight', colorbar=True)
        self.matrix.opts(xaxis=None, yaxis=None, responsive=True, aspect=1, finalize_hooks=[disable_logo])
        self.dyn_matrix = hv.DynamicMap(self.draw_admatrix)
        self.edge_stream = Selection1D(source=self.dyn_matrix)
        self.nodelink = None

    def link_nodelink(self, nodelink):
        self.nodelink = nodelink

    @pm.depends('edge_col', 'size', 'alpha', 'nons_alpha', 'marker')
    def draw_admatrix(self):
        self.matrix.opts(opts.Points(size=self.size, alpha=self.alpha, nonselection_alpha=self.nons_alpha, marker=self.marker, color='weight')).opts(cmap=self.edge_col)
        return self.matrix

    @pm.depends('esel_col', 'esel_alpha')
    def draw_edge_select(self, index):
        starts = self.nodelink.graph.nodes.dimension_values('index')[index]
        if len(starts) == 0:
            return hv.Points([])
        else:
            return self.matrix.select(start=starts.tolist()).opts(opts.Points(alpha=self.esel_alpha, color='weight')).opts(cmap=self.esel_col)

    def start(self):
        return self.dyn_matrix * hv.DynamicMap(self.draw_edge_select, streams=[self.nodelink.node_stream])


# class Dashboard(pm.Parameterized):
# def viewable(self, **kwargs):


def modify_doc(doc):
    # dashboard = Dashboard()
    nodelink = NodeLink(node_link_dataset, name='')
    admatrix = AdMatrix(ad_matrix_dataset, name='')
    nodelink.link_admatrix(admatrix)
    admatrix.link_nodelink(nodelink)
    view1 = nodelink.start()
    view2 = admatrix.start()
    tabs = pn.Tabs()
    tabs.append(("Node-Link", pn.Param(nodelink.param)))
    tabs.append(("Adjacency Matrix", pn.Param(admatrix.param)))
    panel = pn.Row(pn.Column(tabs), view1, view2)
    return panel.server_doc(doc=doc)


server = Server({'/': modify_doc}, port=5006, allow_websocket_origin=['*'])
server.start()
server.show('/')
server.run_until_shutdown()
