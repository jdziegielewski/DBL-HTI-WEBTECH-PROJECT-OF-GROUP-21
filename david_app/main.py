import visualization
import networkx as nx
from bokeh.plotting import curdoc

G = nx.karate_club_graph()

dashboard = visualization.create_dashboard(G)

curdoc().add_root(dashboard)
