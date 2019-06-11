from sklearn.cluster import AgglomerativeClustering
import numpy as np
import pandas as pd
import holoviews as hv

def linkage_clustering(dataframe, linkage_type, number_of_clusters):
    # ALGORITHM
    clustering = AgglomerativeClustering(affinity = "precomputed", linkage = linkage_type, n_clusters = number_of_clusters).fit(dataframe)

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

    index_dataframe = dataframe.index
    final_clustering = []
    for i in range(len(index_dataframe)):
        final_clustering.append(index_dataframe[final_clustering_order[i]])

    #ordered_dataframe = dataframe.copy()
    #for i in range(len(final_clustering)):
    #    for j in range(len(final_clustering)):
    #        ordered_dataframe.iloc[i,j] = dataframe.iloc[final_clustering_order[i],final_clustering_order[j]]

    dataset = create_ad_matrix_dataset(dataframe, final_clustering)

    # OUTPUT
    return dataset

def create_ad_matrix_dataset(dataframe, final_clustering):
    # df.values[[np.arange(df.shape[0])] * 2] = 0
    edge_list = dataframe.stack().reset_index()
    edge_list.columns = ['start', 'end', 'weight']

    edge_list.start = pd.Categorical(edge_list.start, categories = final_clustering)
    edge_list.end = pd.Categorical(edge_list.end, categories = final_clustering)
    edge_list.sort_values(["start", "end"], inplace = True)

    edge_list = edge_list.reset_index()
    edge_list['edge_idx'] = edge_list.index

    dataset = hv.Table(edge_list)
    return dataset
