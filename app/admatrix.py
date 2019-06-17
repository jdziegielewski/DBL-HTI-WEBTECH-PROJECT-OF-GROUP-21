import settings
import operator
import param as pm
import holoviews as hv
import numpy.linalg as la
from holoviews import opts
from holoviews.streams import Selection1D
from scipy.sparse import csgraph, csc_matrix
from sklearn.cluster import AgglomerativeClustering, SpectralClustering


renderer = hv.renderer('bokeh').instance(mode='server', webgl=True)


def make_diagonal(names):
    return [(a, b, 0) for a, b in zip(names, reversed(names))]


def sorted_diagonal(df):
    return make_diagonal(df.index.sort_values())


def agglomerative_clustering(df, linkage, n_clusters=2):
    clustering = AgglomerativeClustering(affinity='precomputed', linkage=linkage, n_clusters=n_clusters).fit(df)
    # clustering.

    clusters = {}
    for i in range(n_clusters):
        clusters[i] = []
        for j in range(len(clustering.labels_)):
            if clustering.labels_[j] == i:
                clusters[i].append(j)

    final_clustering_order = []
    for i in clusters:
        final_clustering_order.append(clusters[i])
    final_clustering_order = [val for sublist in final_clustering_order for val in sublist]

    index_dataframe = df.index
    final_clustering = []
    for i in range(len(index_dataframe)):
        final_clustering.append(index_dataframe[final_clustering_order[i]])

    return make_diagonal(final_clustering)


def spectral_clustering(df):
    clustering = SpectralClustering().fit(df)


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


# def create_ad_matrix_dataset(df, final_clustering):
 #    edge_list = df.stack().reset_index()
 #    edge_list = edge_list[edge_list[0] > 0]
 #    edge_list.columns = ['start', 'end', 'weight']
 #
 #    edge_list.start = pd.Categorical(edge_list.start, categories=final_clustering)
 #    edge_list.end = pd.Categorical(edge_list.end, categories=final_clustering)
 #    edge_list.sort_values(["start", "end"], inplace=True)
 #
 #    dataset = hv.Table(edge_list)
 #    return dataset

class AdMatrix(pm.Parameterized):
    layout_dict = {'Sorted': (lambda self: sorted_diagonal(self.df), None),
                   'Agglomerative Clustering': (lambda self: agglomerative_clustering(self.df, self.agglomerative_linkage.lower(), self.agglomerative_cluster_count),
                                                lambda param: [param.agglomerative_linkage, param.agglomerative_cluster_count]),
                   'Reverse Cuthill-Mckee': (lambda self: reverse_cuthill_mckee(self.df), None),
                   'Fiedler Vector Clustering': (lambda self: fiedler_vector_clustering(self.df), None)}
    layout = pm.Selector(label='Matrix Ordering', objects=layout_dict)
    markers = {'Square': 's', 'Circle': 'o', 'Cross': '+'}
    edge_col = pm.Selector(label='Color', objects=settings.cmaps, default=['blue', 'magenta', 'yellow'])
    marker = pm.Selector(label='Symbol', objects=markers, default='s')
    alpha = pm.Magnitude(label='Alpha', default=0.7)
    nons_alpha = pm.Magnitude(label='Nonselection Alpha', default=0.1)
    size = pm.Number(label='Size', default=5, bounds=(1, 10))
    esel_col = pm.Selector(label='Nodes to Matrix Color', objects=settings.cmaps, default=['green'])
    esel_alpha = pm.Magnitude(label='Nodes to Matrix Alpha', default=0.7)
    agglomerative_linkage = pm.Selector(label='Linkage', objects=['Complete', 'Average', 'Single'], default='Complete')
    agglomerative_cluster_count = pm.Integer(label='Number of clusters', default=2)
    x_axis = pm.Selector(label='Matrix X-Axis Labels', objects={'None': None, 'Top': 'top', 'Bottom': 'bottom'}, default=None)
    y_axis = pm.Selector(label='Matrix Y-Axis Labels', objects={'None': None, 'Left': 'left', 'Right': 'right'}, default=None)
    toolbar = pm.Selector(objects={'Disable': 'disable', 'Above': 'above', 'Below': 'below', 'Left': 'left', 'Right': 'right'},
                          label='Matrix Toolbar', default='above')

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

    @pm.depends('layout', 'agglomerative_linkage', 'agglomerative_cluster_count')
    def draw_ordering(self):
        self.ordering = self.layout[0](self)
        return hv.Points(self.ordering, kdims=['x', 'y'], vdims=['z']).opts(alpha=0, nonselection_alpha=0)

    @pm.depends('edge_col', 'size', 'alpha', 'nons_alpha', 'marker', 'x_axis', 'y_axis', 'toolbar')
    def draw_admatrix(self):
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
        #return dynspread(datashade(hv.Points(self.dataset, kdims=['start', 'end'], vdims=['weight'])))
        # return dynspread(datashade(hv.HeatMap(self.dataset, kdims=['start', 'end'], vdims=['weight']).opts(colorbar=True)))\
            # .opts(xaxis=None, yaxis=None, toolbar='above', responsive=True, aspect=1, finalize_hooks=[disable_logo])\
        #return self.dyn_matrix * hv.DynamicMap(self.draw_edge_select, streams=[self.nodelink.node_stream])
        return self.dyn_order * self.dyn_matrix * hv.DynamicMap(self.draw_edge_select, streams=[self.nodelink.node_stream])
