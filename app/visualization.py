import datashader
import param
import panel as pn
import networkx as nx
import holoviews as hv
from holoviews import opts
from holoviews.element.graphs import layout_nodes
from bokeh.models import Button, Panel, Tabs#, ColumnDataSource
from bokeh.layouts import column, row, WidgetBox
from holoviews.plotting.links import DataLink
from holoviews.operation.datashader import rasterize, datashade, bundle_graph, dynspread
import datashader.transfer_functions as tf

renderer = hv.renderer('bokeh').instance(mode='server', webgl=True)


def heatmap_from_network(G, tools=None):
    adjacency_matrix = nx.to_numpy_matrix(G)

    n = len(G.nodes)
    #triplets = [(i, j, adjacency_matrix[i, j]) for j in range(n) for i in range(n)]

    triplets = []
    for i in range(n):
        for j in range(n):
            triplets.append((i, j, adjacency_matrix[i, j]))

    h = hv.HeatMap(triplets, vdims=['z'])
    h.opts(opts.HeatMap(tools=tools))
    h.opts(xrotation=45, xaxis='top', labelled=[], responsive=True, colorbar=True)
    return h


def nodelink_from_network(G, tools=None):
    h = hv.Graph.from_networkx(G, nx.layout.circular_layout)
    h.opts(opts.Graph(tools=tools))
    h.opts(xaxis=None, yaxis=None, responsive=True)
    return h


def get_column_data(G):
    h = hv.Graph.from_networkx(G, nx.layout.circular_layout)
    return h.columns(dimensions=None)


def get_plot(hv_element):
    return renderer.get_plot(hv_element).state


def create_dashboard(G, filename='None'):
    tools = ['box_select', 'hover', 'tap']

    #view1 = nodelink_from_network(G, tools)
    #view2 = heatmap_from_network(G, tools)

    dataset = hv.Table(G)#ColumnDataSource(G)
    print("TABLE!@#$!@", dataset)

    h = hv.Graph(dataset, kdims=['start', 'end'], vdims=['weight'])
    h = layout_nodes(h, layout=nx.layout.fruchterman_reingold_layout)
    h.opts(opts.Graph(tools=tools))
    h.opts(xaxis=None, yaxis=None, responsive=True)
    view1 = h

    view1_nodes = h.nodes
    view1_nodes.opts(opts.Nodes(tools=tools, size=5))
    view1_nodes.opts(xaxis=None, yaxis=None, responsive=True)

    view1_edges = h.edgepaths
    view1_edges.opts(opts.EdgePaths(tools=tools))
    view1_edges.opts(xaxis=None, yaxis=None, responsive=True)

    h = hv.Points(dataset, kdims=['start', 'end'], vdims=['weight'])
    h.opts(opts.Points(tools=tools, marker='s', size=5))
    h.opts(xrotation=90, xaxis='top', labelled=[], responsive=True, color='weight')
    h.opts(xaxis=None, yaxis=None, responsive=True)
    view2 = h

    view2_bg = hv.HeatMap(dataset, kdims=['start', 'end'], vdims=['weight'])
    view2_bg.opts(opts.HeatMap(tools=tools))
    view2_bg.opts(xrotation=90, xaxis='top', labelled=[], responsive=True)
    view2_bg.opts(xaxis=None, yaxis=None, responsive=True)

    #print("HANDLES::::!)@#(!)@")
    #print(view1.)

    #DataLink(view1_edges, view2)
    #dlink.link()

    hv_layout = datashade(view1_edges) * view1_nodes + view2
    return renderer.app(hv_layout)
    #hv_layout = view1 + view2

    #hv_layout.opts(opts.Layout(shared_datasource=True))
    hv_plot_ = renderer.get_plot(hv_layout)
    hv_plot = hv_plot_.state

    button1 = Button(label='Button 1')
    button2 = Button(label='Button 2')
    button3 = Button(label='Button 3')
    button4 = Button(label='Button 4')
    button5 = Button(label='Button 5')

    button6 = Button(label=filename)

    controls1 = WidgetBox(button1, button2, button3)
    controls2 = WidgetBox(button4, button5)
    controls3 = WidgetBox(button6)

    tab1 = Panel(child=controls1, title='Settings')
    tab2 = Panel(child=controls2, title='More settings')
    tab3 = Panel(child=controls3, title='File info')
    tabs = Tabs(tabs=[tab1, tab2, tab3])

    column1 = column(tabs, sizing_mode='scale_height')

    dashboard = row(column1, hv_plot, sizing_mode='scale_both')
    return dashboard
