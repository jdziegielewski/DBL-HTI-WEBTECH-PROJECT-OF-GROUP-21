import networkx as nx
import numpy as np
import numpy.linalg as la
import pandas as pd
import holoviews as hv
from scipy.sparse import csgraph
import operator

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

	dataset = create_ad_matrix_dataset(df, final_clustering)

	return dataset

def create_ad_matrix_dataset(df, final_clustering):
    edge_list = df.stack().reset_index()
    edge_list = edge_list[edge_list[0] > 0]
    edge_list.columns = ['start', 'end', 'weight']

    edge_list.start = pd.Categorical(edge_list.start, categories=final_clustering)
    edge_list.end = pd.Categorical(edge_list.end, categories=final_clustering)
    edge_list.sort_values(["start", "end"], inplace=True)

    dataset = hv.Table(edge_list)
    return dataset
