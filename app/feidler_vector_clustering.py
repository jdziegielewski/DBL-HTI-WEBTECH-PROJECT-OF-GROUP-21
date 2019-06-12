import networkx as nx
import numpy as np


def fiedler_vector_clustering(df):
	### INPUT ###
	G = nx.Graph()
	G.add_edges_from(df)

	### ALGORITHM ###
	fiedler=fiedler_vector(G, weight='weight', normalized=False, tol=1e-08, method='tracemin')
	return fiedler
	  