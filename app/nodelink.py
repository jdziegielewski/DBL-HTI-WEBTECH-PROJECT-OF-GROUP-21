import settings
import param as pm
import networkx as nx
import holoviews as hv
import datashader as ds
from holoviews import opts
from holoviews.streams import Selection1D
from holoviews.element.graphs import layout_nodes
from holoviews.operation.datashader import datashade, aggregate, bundle_graph, dynspread, shade
from collections import OrderedDict


class NodeLink(pm.Parameterized):
    layout_dict = OrderedDict([('Circular', nx.layout.circular_layout),
                               ('Fruchterman-Reingold', nx.layout.fruchterman_reingold_layout),
                               ('Kamada-Kawai', nx.layout.kamada_kawai_layout),
                               ('Spring', nx.layout.spring_layout),
                               ('Spectral', nx.drawing.spectral_layout)])
    layout = pm.Selector(label='Node-Link Layout', objects=layout_dict)

    edge_col = pm.Selector(label='Edge Color', objects=settings.cmaps)
    edge_alpha = pm.Integer(label='Edge Alpha', default=200, bounds=(0, 255))

    nsel_col = pm.Selector(label='Nodes to Edges Color', objects=settings.cmaps, default=['green'])
    nsel_alpha = pm.Integer(label='Nodes to Edges Alpha', default=200, bounds=(0, 255))

    esel_col = pm.Selector(label='Matrix to Edges Color', objects=settings.cmaps, default=['purple'])
    esel_alpha = pm.Integer(label='Matrix to Edges Alpha', default=200, bounds=(0, 255))

    node_size = pm.Number(label='Node Size', default=5, bounds=(1, 10))
    node_col = pm.Color(label='Node Fill Color', default='#2b9ad0')
    line_col = pm.Color(label='Node Line Color', default='#ffffff')
    node_alpha = pm.Magnitude(label='Node Alpha', default=1)

    bundle = pm.Selector(label='Edge Bundling', objects=OrderedDict([('Off', False), ('On', True)]))
    rendering_method = pm.Selector(label='Rendering Method', objects=OrderedDict([('Datashaded', 1), ('Interactive', 0)]))

    toolbar = pm.Selector(objects=OrderedDict([('Above', 'above'), ('Below', 'below'), ('Left', 'left'), ('Right', 'right'), ('Disable', 'disable')]), label='Node-Link Toolbar', default='above')

    def __init__(self, data, **params):
        super().__init__(**params)
        self.dataset = data
        self.graph = hv.Graph(data, kdims=['start', 'end'], vdims=['weight', 'edge_idx'])
        self.graph = layout_nodes(self.graph, layout=nx.layout.circular_layout)
        self.bundled_graph = None
        self.edges = self.graph.edgepaths
        self.edges = self.edges.add_dimension('weight', dim_pos=1, dim_val=self.dataset['weight'], vdim=True)
        self.nodes = self.graph.nodes
        self.nodes.opts(opts.Nodes(tools=settings.tools))
        self.last_layout = self.layout
        self.last_bundle = False
        self.dyn_nodes = hv.DynamicMap(self.draw_nodes)
        self.node_stream = Selection1D(source=self.dyn_nodes)
        self.dyn_node_select = None
        self.dyn_edge_select = None
        self.admatrix = None
        self.jobs = None

    def link_admatrix(self, admatrix):
        self.admatrix = admatrix

    def update_layout(self):
        new_graph = None
        if self.last_layout != self.layout:
            self.last_layout = self.layout
            self.graph = layout_nodes(self.graph, layout=self.last_layout)
            new_graph = self.graph
            self.param.set_param(bundle=False)
        elif self.last_bundle != self.bundle:
            self.last_bundle = self.bundle
            if self.last_bundle:
                self.bundled_graph = bundle_graph(self.graph)
                new_graph = self.bundled_graph
            else:
                new_graph = self.graph
        if new_graph:
            self.edges = new_graph.edgepaths
            if not self.last_bundle:
                self.edges = self.edges.add_dimension('weight', dim_pos=1, dim_val=self.dataset['weight'], vdim=True)
            self.nodes = new_graph.nodes
            self.nodes.opts(opts.Nodes(tools=settings.tools))

    def get_graph(self):
        return self.bundled_graph if self.bundle else self.graph

    @pm.depends('layout', 'edge_col', 'edge_alpha')
    def draw_edges(self):
        self.admatrix.param.set_param(edge_col=self.edge_col)
        self.update_layout()
        if not self.bundle:
            self.edges.opts(opts.EdgePaths(color='weight', cmap=self.edge_col, alpha=self.edge_alpha, line_width=hv.dim('weight')))
        return self.edges

    @pm.depends('layout', 'node_col', 'line_col', 'node_size', 'node_alpha')
    def draw_nodes(self):
        self.nodes.opts(opts.Nodes(
            color=self.node_col,
            line_color=self.line_col,
            size=self.node_size,
            alpha=self.node_alpha))
        return self.nodes

    @pm.depends('layout')
    def draw_node_select(self, index):
        starts = self.get_graph().nodes.dimension_values('index')[index]
        if len(starts) == 0:
            return hv.Curve(([0], [0]))
        else:
            return self.get_graph().select(start=starts.tolist())

    @pm.depends('layout')
    def draw_edge_select(self, index=None):
        if not index:
            return hv.Curve(([0], [0]))
        else:
            return self.get_graph().select(edge_idx=index)

    @pm.depends('toolbar', 'rendering_method', 'bundle')
    def view(self):
        self.update_layout()
        dyn_edges = hv.DynamicMap(self.draw_edges)
        if self.rendering_method == 1:
            if not self.bundle:
                dyn_edges.opts(colorbar=True)
                dyn_edges = aggregate(dyn_edges, aggregator=ds.mean('weight'), precompute=True)
                dyn_edges = shade(dyn_edges, cmap=self.param.edge_col, alpha=self.param.edge_alpha)
            else:
                dyn_edges = datashade(dyn_edges, cmap=self.param.edge_col, alpha=self.param.edge_alpha, precompute=True)
        self.dyn_node_select = hv.DynamicMap(self.draw_node_select, streams=[self.node_stream])
        self.dyn_edge_select = hv.DynamicMap(self.draw_edge_select, streams=[self.admatrix.edge_stream])
        hv_plot = \
            dyn_edges \
            .opts(xaxis=None, yaxis=None, toolbar=self.toolbar, responsive=True,
                  aspect=1, finalize_hooks=[settings.disable_logo]) \
            * self.dyn_nodes \
            * dynspread(datashade(self.dyn_node_select, cmap=self.param.nsel_col, alpha=self.param.nsel_alpha, precompute=False), max_px=100) \
            * dynspread(datashade(self.dyn_edge_select, cmap=self.param.esel_col, alpha=self.param.esel_alpha, precompute=False), max_px=100)
        return hv_plot
