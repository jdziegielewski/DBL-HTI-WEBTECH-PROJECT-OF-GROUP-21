from sklearn.cluster import AgglomerativeClustering
import numpy as np
import pandas as pd

def linkage_clustering(linkage_type, number_of_clusters):
    # INPUT
    dataframe = create_dataframe(filename)
    number_of_clusters = 3
    linkage_type = "complete"

    # ALGORITHM
    clustering = AgglomerativeClustering(affinity = "precomputed", linkage = linkage_type, n_clusters = number_of_clusters).fit(dataframe)

    clusters = {}
    for i in range(number_of_clusters):
        clusters[i] = []
        for j in range(len(clustering.labels_)):
            if clustering.labels_[j] == i:
                clusters[i].append(j)

    final_clustering = []
    for i in clusters:
        final_clustering.append(clusters[i])
    final_clustering = [val for sublist in final_clustering for val in sublist]

    ordered_dataframe = dataframe.copy()
    for i in range(len(final_clustering)):
        for j in range(len(final_clustering)):
            ordered_dataframe.iloc[i,j] = dataframe.iloc[final_clustering[i],final_clustering[j]]

    edge_list = create_edge_list(ordered_dataframe)
    dataset = hv.Table(edge_list)

    # OUTPUT
    return dataset
