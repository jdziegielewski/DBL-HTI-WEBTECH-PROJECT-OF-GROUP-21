import os
import json
import sys
import sidebar
import colorcet
import cloudpickle
import numpy as np
import pandas as pd
import holoviews as hv
from bokeh.server.server import Server

renderer = hv.renderer('bokeh').instance(mode='server', webgl=True)


def create_node_link_dataset(df):
    # df.values[[np.arange(df.shape[0])] * 2] = 0
    edge_list = df.stack().reset_index()
    edge_list = edge_list[edge_list[0] > 0]
    edge_list.columns = ['start', 'end', 'weight']
    edge_list = edge_list.reset_index()

    index_edge_list = np.unique(edge_list[["start", "end"]].values)
    index_dataframe = df.index
    if len(index_edge_list) != len(index_dataframe):
        diff = set(index_dataframe) - set(index_edge_list)
        for i in diff:
            edge_list = edge_list.append({"start": i, "end": i, "weight": 0}, ignore_index=True)
            
        edge_list['edge_idx'] = edge_list.index
    dataset = hv.Table(edge_list)
    return dataset

def create_ad_matrix_dataset(df):
    # df.values[[np.arange(df.shape[0])] * 2] = 0
    edge_list = df.stack().reset_index()
    edge_list.columns = ['start', 'end', 'weight']
    edge_list = edge_list.reset_index()

    edge_list['edge_idx'] = edge_list.index
    dataset = hv.Table(edge_list)
    return dataset


#For loading DataFrames
def load_obj(name):
    with open('uploads/' + name + '.pkl', 'rb') as file:
        return cloudpickle.load(file)


filename = sys.argv[1]
#path = os.path.join("uploads", filename)
dataframe = load_obj(filename)

# dataframe = load_local_adm(path)
node_link_dataset = create_node_link_dataset(dataframe)
ad_matrix_dataset = create_ad_matrix_dataset(dataframe)


def modify_doc(doc):
    panel = sidebar.create_sidebar(node_link_dataset, ad_matrix_dataset, dataframe)
    return panel.server_doc(doc=doc)


server = Server({'/': modify_doc}, port=5006, allow_websocket_origin=['*'])
server.start()
server.run_until_shutdown()
