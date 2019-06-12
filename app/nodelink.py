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
from holoviews.operation import decimate
from collections import OrderedDict as odict

renderer = hv.renderer('bokeh').instance(mode='server', webgl=True)

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
    edge_bundle = pm.Selector(label='Edge Bundling', objects=['Off', 'On'])
    rendering_method = pm.Selector(label='Rendering Method', objects=['Interactive', 'Datashaded'])

    def __init__(self, data, **params):
        super().__init__(**params)
        self.dataset = data
        self.graph = hv.Graph(data, kdims=['start', 'end'], vdims=['weight', 'edge_idx'])
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
        self.jobs = None

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
                self.edges = self.edges.add_dimension('weight', 0, self.dataset.dframe(dimensions=['weight'])['weight'],
                                                      vdim=True)
            self.nodes = new_graph.nodes
            self.nodes.opts(opts.Nodes(tools=tools))

    def get_graph(self):
        return self.bundled_graph if self.bundle else self.graph

    @pn.depends('layout', 'edge_col', 'bundle', 'rendering_method')
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
        print(index)
        if not index:
            return hv.Curve(([0], [0]))
        else:
            return self.get_graph().select(edge_idx=index)

    @pn.depends('rendering_method')
    def view(self):
        dyn_edges = self.dyn_edges
        if self.rendering_method == 'Datashaded':
            dyn_edges = datashade(self.dyn_edges, cmap=self.param.edge_col, alpha=self.param.edge_alpha, precompute=True)

        self.dyn_edge_select = hv.DynamicMap(self.draw_edge_select, streams=[self.admatrix.edge_stream])
        hv_plot = \
            dyn_edges \
            .opts(xaxis=None, yaxis=None, toolbar='above', responsive=True, aspect=1, finalize_hooks=[disable_logo]) \
            * self.dyn_nodes \
            * dynspread(datashade(self.dyn_node_select, cmap=self.param.nsel_col, alpha=self.param.nsel_alpha, precompute=True), max_px=100) \
            #* dynspread(datashade(self.dyn_edge_select, cmap=self.param.esel_col, alpha=self.param.esel_alpha, precompute=True), max_px=100)
        #hv_plot.opts(bgcolor=self.param.bg_col)
        return hv_plot