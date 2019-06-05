import networkx as nx
import holoviews as hv
from holoviews import opts
from bokeh.models import Button, Panel, Tabs
from bokeh.layouts import column, row, WidgetBox

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
    h.opts(xrotation=45, xaxis='top', labelled=[], responsive=True)
    return h


def nodelink_from_network(G, tools=None):
    h = hv.Graph.from_networkx(G, nx.layout.circular_layout)
    h.opts(opts.Graph(tools=tools))
    h.opts(xaxis=None, yaxis=None, responsive=True)
    return h


def get_plot(hv_element):
    return renderer.get_plot(hv_element).state


def create_dashboard(G, filename='None'):
    tools = ['box_select', 'hover']

    view1 = nodelink_from_network(G, tools)
    view2 = heatmap_from_network(G, tools)

    hv_plot = get_plot(view1 + view2)

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

