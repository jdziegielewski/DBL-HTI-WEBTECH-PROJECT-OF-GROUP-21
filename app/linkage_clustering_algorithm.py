import networkx as nx
from sklearn.cluster import AgglomerativeClustering
import numpy as np

def linkage_clustering(G, linkage_type, number_of_clusters):
    ### INPUT ###
    adjacency_matrix = nx.to_numpy_matrix(G)
    linkage_type = "complete"  ### single/complete/average
    number_of_clusters = 3

    ### ALGORITHM ###
    clustering = AgglomerativeClustering(affinity = "precomputed", linkage = linkage_type, n_clusters = number_of_clusters).fit(adjacency_matrix)

    n = len(G.nodes)

    clusters = {}
    for i in range(number_of_clusters):
        clusters[i] = []
        for j in range(n):
            if clustering.labels_[j] == i:
                clusters[i].append(j)

    final_clustering = []
    for i in clusters:
        final_clustering.append(clusters[i])
    final_clustering = [val for sublist in final_clustering for val in sublist]

    ordered_matrix = adjacency_matrix.copy()
    for i in range(n):
        for j in range(n):
            ordered_matrix[i,j] = adjacency_matrix[final_clustering[i],final_clustering[j]]

    ### OUTPUT ###
    return ordered_matrix
