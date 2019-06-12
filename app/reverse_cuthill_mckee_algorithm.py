import pandas as pd
from scipy.sparse import csgraph, csc_matrix
import holoviews as hv

def reverse_cuthill_mckee(df):
    CSC = csc_matrix(df)

    final_clustering_order = csgraph.reverse_cuthill_mckee(CSC)

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
