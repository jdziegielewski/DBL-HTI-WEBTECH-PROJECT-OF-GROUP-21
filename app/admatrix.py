import colorcet
import param as pm
import holoviews as hv
import datashader as ds
from holoviews import opts
from holoviews.streams import Selection1D
from holoviews.operation.datashader import datashade, dynspread, shade
import linkage_clustering_algorithm

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

class AdMatrix(pm.Parameterized):
    layout = pm.Selector(label='Matrix Ordering', objects=['None', 'Clustering'], default='None')
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

    def __init__(self, data, dataframe, **params):
        super().__init__(**params)
        self.dataset = data
        self.dataframe = dataframe
        self.matrix = hv.Points(data, kdims=['start', 'end'], vdims=['weight'])
        self.matrix.redim(weight=dict(range=(0.1, 10)))
        self.matrix.opts(opts.Points(tools=tools, toolbar='above'))
        self.matrix.opts(xrotation=90, xaxis='top', labelled=[], color='weight', colorbar=True)
        self.matrix.opts(xaxis=None, yaxis=None, responsive=True, aspect=1, finalize_hooks=[disable_logo])
        self.dyn_matrix = hv.DynamicMap(self.draw_admatrix)
        self.edge_stream = Selection1D(source=self.dyn_matrix)
        self.nodelink = None
        self.last_layout = 'None'

    def link_nodelink(self, nodelink):
        self.nodelink = nodelink

    def update_layout(self):
        if self.last_layout is not self.layout:
            self.last_layout = self.layout
            if self.last_layout is 'Clustering':
                new_data = linkage_clustering_algorithm.linkage_clustering(self.dataframe, "ward", 3)
                self.matrix = hv.Points(new_data, kdims=['start', 'end'], vdims=['weight'])
            else:
                self.matrix = hv.Points(self.dataset, kdims=['start', 'end'], vdims=['weight'])
            self.matrix.opts(opts.Points(tools=tools, toolbar='above'))
            self.matrix.opts(xrotation=90, xaxis='top', labelled=[], color='weight', colorbar=True)
            self.matrix.opts(xaxis=None, yaxis=None, responsive=True, aspect=1, finalize_hooks=[disable_logo])

    @pm.depends('edge_col', 'size', 'alpha', 'nons_alpha', 'marker', 'layout')
    def draw_admatrix(self):
        self.update_layout()
        self.matrix.opts(opts.Points(size=self.size, alpha=self.alpha, nonselection_alpha=self.nons_alpha,
                                     marker=self.marker, color='weight')).opts(cmap=self.edge_col)
        self.matrix.opts(cmap=self.edge_col)
        return self.matrix

    @pm.depends('esel_col', 'esel_alpha')
    def draw_edge_select(self, index):
        starts = self.nodelink.graph.nodes.dimension_values('index')[index]
        if len(starts) == 0:
            return hv.Points([])
        else:
            return self.matrix.select(start=starts.tolist()).opts(opts.Points(alpha=self.esel_alpha, color='weight')).opts(cmap=self.esel_col)

    def start(self):
        #return dynspread(datashade(hv.Points(self.dataset, kdims=['start', 'end'], vdims=['weight'])))
        # return dynspread(datashade(hv.HeatMap(self.dataset, kdims=['start', 'end'], vdims=['weight']).opts(colorbar=True)))\
            # .opts(xaxis=None, yaxis=None, toolbar='above', responsive=True, aspect=1, finalize_hooks=[disable_logo])\
        return self.dyn_matrix * hv.DynamicMap(self.draw_edge_select, streams=[self.nodelink.node_stream])

    def test_trigger(self, value):
        print(value)