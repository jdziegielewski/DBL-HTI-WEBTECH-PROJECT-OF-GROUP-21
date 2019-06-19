import settings
import operator
import param as pm
import holoviews as hv
import numpy.linalg as la
from holoviews import opts
from holoviews.streams import Selection1D
from scipy.sparse import csgraph, csc_matrix
from sklearn.cluster import AgglomerativeClustering, SpectralClustering, AffinityPropagation
from collections import OrderedDict

def make_diagonal(names):
    return [(a, b, 0) for a, b in zip(names, reversed(names))]


def sorted_diagonal(df):
    return make_diagonal(df.index.sort_values())


def agglomerative_clustering(df, affinity, linkage, n_clusters=2):
    clustering = AgglomerativeClustering(affinity=affinity, linkage=linkage, n_clusters=n_clusters).fit(df)
    ordering = [name for _, name in sorted(zip(clustering.labels_, df.index))]
    return make_diagonal(ordering)


def affinity_propagation(df, affinity, damping, max_iter):
    clustering = AffinityPropagation(affinity=affinity, damping=damping, max_iter=max_iter).fit(df)
    ordering = [name for _, name in sorted(zip(clustering.labels_, df.index))]
    return make_diagonal(ordering)


def spectral_clustering(df, n_clusters=2):
    clustering = SpectralClustering(affinity='precomputed', n_clusters=n_clusters).fit(df)
    ordering = [name for _, name in sorted(zip(clustering.labels_, df.index))]
    return make_diagonal(ordering)


def reverse_cuthill_mckee(df):
    csc = csc_matrix(df)
    ordering = csgraph.reverse_cuthill_mckee(csc)
    indices = [df.index[i] for i in ordering]
    return make_diagonal(indices)


def fiedler_vector_clustering(df):
    laplacian = csgraph.laplacian(df, normed=False)
    eigenvalues, eigenvectors = la.eig(laplacian)

    seen = {}
    unique_eigenvalues = []
    for (x, y) in zip(eigenvalues, eigenvectors):
        if x in seen:
            continue
        seen[x] = 1
        unique_eigenvalues.append((x, y))

    fiedler_vector = sorted(unique_eigenvalues)[1][1]

    fiedler_labels = {}
    for i in range(len(fiedler_vector)):
        fiedler_labels[df.index[i]] = fiedler_vector[i]
    fiedler_labels = sorted(fiedler_labels.items(), key=operator.itemgetter(1))

    final_clustering = [labels[0] for labels in fiedler_labels]
    return make_diagonal(final_clustering)


class AdMatrix(pm.Parameterized):
    layout_dict = OrderedDict([('Default', (lambda self: make_diagonal(self.df.index), None)),
                               ('Sorted', (lambda self: sorted_diagonal(self.df), None)),
                               ('Agglomerative Clustering', (lambda self: agglomerative_clustering(self.df, self.affinity, self.agglomerative_linkage.lower(), self.agglomerative_cluster_count), lambda param: [param.affinity, param.agglomerative_linkage, param.agglomerative_cluster_count])),
                               ('Affinity Propagation', (lambda self: affinity_propagation(self.df, self.affinity, self.affinity_damping, self.max_iteration), lambda param: [param.affinity, param.affinity_damping, param.max_iteration])),
                               ('Reverse Cuthill-Mckee', (lambda self: reverse_cuthill_mckee(self.df), None)),
                               ('Spectral Clustering', (lambda self: spectral_clustering(self.df), lambda param: [param.agglomerative_cluster_count])),
                               ('Fiedler Vector Clustering', (lambda self: fiedler_vector_clustering(self.df), None))])
    layout = pm.Selector(label='Matrix Ordering', objects=layout_dict)
    edge_col = pm.Selector(label='Color', objects=settings.cmaps)
    markers = OrderedDict([('Square', 's'), ('Circle', 'o'), ('Cross', '+')])
    marker = pm.Selector(label='Symbol', objects=markers)
    alpha = pm.Magnitude(label='Alpha', default=0.5)
    nons_alpha = pm.Magnitude(label='Nonselection Alpha', default=0.1)
    size = pm.Number(label='Size', default=5, bounds=(1, 10))
    esel_col = pm.Selector(label='Nodes to Matrix Color', objects=settings.cmaps, default=['green'])
    esel_alpha = pm.Magnitude(label='Nodes to Matrix Alpha', default=0.7)
    agglomerative_linkage = pm.Selector(label='Linkage', objects=['Complete', 'Average', 'Single'])
    agglomerative_cluster_count = pm.Integer(label='Number of clusters', default=2)
    affinity = pm.Selector(label='Affinity', objects=OrderedDict([('Pre-computed', 'precomputed'), ('Euclidean', 'euclidean')]))
    affinity_damping = pm.Number(label='Damping', default=0.5, bounds=(0.5, 1.0))
    max_iteration = pm.Integer(label='Maximum Iterations', default=50, bounds=(10, 200))
    x_axis = pm.Selector(label='Matrix X-Axis Labels', objects=OrderedDict([('None', None), ('Top', 'top'), ('Bottom', 'bottom')]))
    y_axis = pm.Selector(label='Matrix Y-Axis Labels', objects=OrderedDict([('None', None), ('Left', 'left'), ('Right', 'right')]))
    toolbar = pm.Selector(objects=OrderedDict([('Above', 'above'), ('Below', 'below'), ('Left', 'left'), ('Right', 'right'), ('Disable', 'disable')]), label='Matrix Toolbar')

    def __init__(self, edges, df, **params):
        super().__init__(**params)
        self.df = df
        self.edges = edges
        self.nodelink = None
        self.last_layout = 'None'
        self.ordering = sorted_diagonal(df)
        self.dyn_order = hv.DynamicMap(self.draw_ordering)
        self.matrix = hv.Points(edges, kdims=['start', 'end'], vdims=['start', 'end', 'weight'])
        self.matrix.opts(opts.Points(tools=settings.tools, toolbar='above'))
        self.matrix.opts(xrotation=90, xaxis=None, yaxis=None, labelled=[], color='weight', colorbar=True)
        self.matrix.opts(responsive=True, aspect=1, finalize_hooks=[settings.disable_logo])
        self.dyn_matrix = hv.DynamicMap(self.draw_admatrix)
        self.edge_stream = Selection1D(source=self.dyn_matrix)

    def link_nodelink(self, nodelink):
        self.nodelink = nodelink

    @pm.depends('layout', 'agglomerative_linkage', 'agglomerative_cluster_count', 'affinity_damping', 'max_iteration', 'affinity')
    def draw_ordering(self):
        self.ordering = self.layout[0](self)
        return hv.Points(self.ordering, kdims=['x', 'y'], vdims=['z']).opts(alpha=0, nonselection_alpha=0)

    @pm.depends('edge_col', 'size', 'alpha', 'nons_alpha', 'marker', 'x_axis', 'y_axis', 'toolbar')
    def draw_admatrix(self):
        self.nodelink.param.set_param(edge_col=self.edge_col)
        self.matrix.opts(opts.Points(size=self.size,
                                     alpha=self.alpha,
                                     xaxis=self.x_axis,
                                     yaxis=self.y_axis,
                                     toolbar=self.toolbar,
                                     nonselection_alpha=self.nons_alpha,
                                     marker=self.marker,
                                     color='weight'))
        self.matrix.opts(cmap=self.edge_col)
        return self.matrix

    @pm.depends('esel_col', 'esel_alpha')
    def draw_edge_select(self, index):
        starts = self.nodelink.graph.nodes.dimension_values('index')[index]
        if len(starts) == 0:
            return hv.Points([])
        else:
            return self.matrix.select(start=starts.tolist()).opts(opts.Points(alpha=self.esel_alpha, color='weight')).opts(cmap=self.esel_col)

    def view(self):
        return self.dyn_order * self.dyn_matrix * hv.DynamicMap(self.draw_edge_select, streams=[self.nodelink.node_stream])
        #return dynspread(datashade(hv.Points(self.dataset, kdims=['start', 'end'], vdims=['weight'])))
        # return dynspread(datashade(hv.HeatMap(self.dataset, kdims=['start', 'end'], vdims=['weight']).opts(colorbar=True)))\
            # .opts(xaxis=None, yaxis=None, toolbar='above', responsive=True, aspect=1, finalize_hooks=[disable_logo])\
        #return self.dyn_matrix * hv.DynamicMap(self.draw_edge_select, streams=[self.nodelink.node_stream])
