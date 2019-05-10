import numpy as np
import networkx as nx
import holoviews as hv
from bokeh.plotting import figure
from bokeh.models import HoverTool, ColumnDataSource
from holoviews import opts


def plot_network(G):
    N = len(G.nodes)

    adjacency_matrix = nx.to_numpy_matrix(G)

    weights = []
    for i in range(N):
        for j in range(N):
            idx = i * N + j
            weights.append((i, j, adjacency_matrix[i, j], idx, False))

    source = ColumnDataSource(
        data=dict(
            edges=weights
        )
    )

    heatmap = hv.HeatMap(weights, vdims=['z', 'idx', 'selected'])
    print("Heatmap columns:", heatmap.columns())
    #heatmap.opts(opts.HeatMap(tools=['hover', 'box_select'], width=325))
    return heatmap, source


def plot_network_colored(G):
    N = len(G.nodes)

    adjacency_matrix = nx.to_numpy_matrix(G)

    weights = []
    for i in range(N):
        for j in range(N):
            weight = adjacency_matrix[i, j]
            weights.append((i, j, weight))

    color = []
    #for i in selected:


    heatmap = hv.HeatMap(weights, vdims=['z'])
    heatmap.opts(opts.HeatMap(tools=['hover', 'box_select'], width=325))
    return heatmap, weights


def plot(G):
    adjacency_matrix = nx.to_numpy_matrix(G)

    #nodes = G.nodes
    N = len(G.nodes)

    names = [str(i) for i in range(1, N+1)]

    weights = np.empty((N, N))
    for edge in G.edges:
        source = edge[0]
        target = edge[1]
        weights[source, target] = 1
        weights[target, source] = 1

    x_name = []
    y_name = []
    color = []
    alpha = []
    for i, n1 in enumerate(names):
        for j, n2 in enumerate(names):
            x_name.append(n1)
            y_name.append(n2)
            a = min(adjacency_matrix[i, j], 0.9) + 0.1
            alpha.append(a)
            color.append('lightgrey')

    source = ColumnDataSource(
        data=dict(
            x_name=x_name,
            y_name=y_name,
            colors=color,
            alphas=alpha,
            weights=weights.flatten(),
        )
    )

    p = figure(title="Karate Club Data",
               x_axis_location="above", tools="hover, pan, box_select, wheel_zoom, reset",
               x_range=list(reversed(names)), y_range=names,
               plot_width=300, plot_height=300)

    p.rect('x_name', 'y_name', 0.9, 0.9, source=source, color='colors', alpha='alphas', line_color=None)

    p.grid.grid_line_color = None
    p.axis.axis_line_color = None
    p.axis.major_tick_line_color = None
    p.axis.major_label_text_font_size = "5pt"
    p.axis.major_label_standoff = 0
    p.xaxis.major_label_orientation = np.pi/2

    hover = p.select(dict(type=HoverTool))
    hover.tooltips = [
        ('Edge', '@y_name, @x_name'),
        ('Weight', '@weights'),
    ]

    return p