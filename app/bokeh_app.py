import os
import json
import sys
import sidebar
import cloudpickle
import numpy as np
import pandas as pd
import holoviews as hv
from bokeh.server.server import Server

renderer = hv.renderer('bokeh').instance(mode='server', webgl=True)


def create_node_link_dataset(df):
    # df.values[[np.arange(df.shape[0])] * 2] = 0

    edge_list_ = pd.DataFrame(columns=['start', 'end', 'weight'])
    for i in df.index:
        edge_list_ = edge_list_.append({'start': i, 'end': i, 'weight': 0}, ignore_index=True)

    edge_list = df.stack().reset_index()
    edge_list = edge_list[edge_list[0] > 0]
    edge_list.columns = ['start', 'end', 'weight']
    edge_list = edge_list.reset_index()

    for index, row in edge_list.iterrows():
        edge_list_.append({'start': edge_list.iloc[index]['start'], 'end': edge_list.iloc[index]['start'], 'weight': edge_list.iloc[index]['start']}, ignore_index=True)

    edge_list_['edge_idx'] = edge_list_.index
    dataset = hv.Table(edge_list_)
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
ad_matrix_dataset = node_link_dataset #create_ad_matrix_dataset(dataframe)


def modify_doc(doc):
    panel = sidebar.create_sidebar(node_link_dataset, ad_matrix_dataset, dataframe)
    return panel.server_doc(doc=doc)


server = Server({'/': modify_doc}, port=5006, allow_websocket_origin=['*'])
server.start()
server.run_until_shutdown()
