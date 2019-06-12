from sklearn.cluster import AgglomerativeClustering
import numpy as np
import pandas as pd
import holoviews as hv

def linkage_clustering(df, linkage_type, number_of_clusters):
    clustering = AgglomerativeClustering(affinity="precomputed", linkage=linkage_type, n_clusters=number_of_clusters)\
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
