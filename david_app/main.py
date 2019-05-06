import data.examples
import adjacencymatrix
import nodelink
import networkx as nx
from bokeh.plotting import curdoc
import holoviews as hv
import numpy as np
from holoviews import streams


renderer = hv.renderer('bokeh').instance(mode='server')

G = nx.karate_club_graph()

hv_nodelink = nodelink.plot_network(G)

# Declare some points
#points = hv.Points(G.nodes)

# Declare points as source of selection stream
selection = streams.Selection1D(source=hv_nodelink)


# Write function that uses the selection indices to slice points and compute stats
def selected_info(index):
    arr = hv_nodelink.nodes.array()[index]
    #if index:
        #label = 'Mean x, y: %.3f, %.3f' % tuple(arr.mean(axis=0))
    #else:
        #label = 'No selection'
    return hv_nodelink.nodes.clone(arr)


# Combine points and DynamicMap
#selected_points = hv.DynamicMap(selected_info, streams=[selection])
#hv_plot = points.opts(tools=['box_select', 'lasso_select']) + selected_points

hv_nodelink_selected = hv.DynamicMap(selected_info, streams=[selection])
hv_nodelink_arrows = nodelink.plot_network(G)

hv_plot = hv_nodelink.opts(tools=['box_select', 'lasso_select']) + hv_nodelink_selected
hv_plot += hv_nodelink_arrows.opts(directed=True, arrowhead_length=0.04)
#hv_plot += adjacencymatrix.plot_network(G)

curdoc().add_root(renderer.get_plot(hv_plot).state)
curdoc().add_root(adjacencymatrix.plot(G))
