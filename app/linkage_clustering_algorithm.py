from sklearn.cluster import AgglomerativeClustering
import numpy as np
import pandas as pd
import holoviews as hv


def sorted(df):
    names = df.index.sort_values()
    ordering = [(a, b, 0) for a, b in zip(names, reversed(names))]
    return ordering


def linkage_clustering(df, linkage_type, number_of_clusters):
    # ALGORITHM
    clustering = AgglomerativeClustering(affinity="euclidean", linkage=linkage_type, n_clusters=number_of_clusters)\
        .fit(df)

    clusters = {}
    for i in range(number_of_clusters):
        clusters[i] = []
        for j in range(len(clustering.labels_)):
            if clustering.labels_[j] == i:
                clusters[i].append(j)

    final_clustering_order = []
    for i in clusters:
        final_clustering_order.append(clusters[i])
    final_clustering_order = [val for sublist in final_clustering_order for val in sublist]

    index_dataframe = df.index
    final_clustering = []
    for i in range(len(index_dataframe)):
        final_clustering.append(index_dataframe[final_clustering_order[i]])

    print("!!!!!!", final_clustering, "!!!!!!!")

    #ordered_dataframe = dataframe.copy()
    #for i in range(len(final_clustering)):
    #    for j in range(len(final_clustering)):
    #        ordered_dataframe.iloc[i,j] = dataframe.iloc[final_clustering_order[i],final_clustering_order[j]]

    #dataset = create_ad_matrix_dataset(df, final_clustering)

    # OUTPUT
    ordering = [(a, b, 0) for a, b in zip(final_clustering, reversed(final_clustering))]
    return ordering
