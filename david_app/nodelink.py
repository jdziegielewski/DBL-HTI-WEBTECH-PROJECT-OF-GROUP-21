import networkx as nx
import holoviews as hv
from holoviews.operation.datashader import bundle_graph, datashade


def plot_network(self, layout=nx.layout.circular_layout):
    """

    :param self: NetworkX Graph
    :param layout: Layout object
    """
    graph = hv.Graph.from_networkx(self, layout)
    #graph = bundle_graph(graph)
    #plot = hv.render(graph, backend='bokeh')
    #return plot
    return graph


def shade_network(self, layout=nx.layout.circular_layout):
    """

    :param self: NetworkX Graph
    :param layout: Layout object
    """
    print("Datashading start")
    graph = hv.Graph.from_networkx(self, layout)
    bundled_graph = bundle_graph(graph)
    shaded_graph = datashade(bundled_graph).opts(plot=dict(width=800, height=600, sizing_mode='scale_both'))
    print("Datashading done")
    return shaded_graph
