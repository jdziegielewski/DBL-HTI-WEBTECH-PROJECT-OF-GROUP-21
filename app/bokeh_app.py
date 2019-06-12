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
    names = df.index

    edge_list = df.stack().reset_index()
    edge_list = edge_list[edge_list[0] > 0]
    edge_list.columns = ['start', 'end', 'weight']
    edge_list = edge_list.reset_index()

    included_names = np.unique(edge_list[['start', 'end']].values)

    for n in names:
        edge_list.append({'start': n, 'end': n, 'weight': 1}, ignore_index=True)

    #for index, row in edge_list.iterrows():
        #edge_list_.append({'start': edge_list.iloc[index]['start'], 'end': edge_list.iloc[index]['start'], 'weight': edge_list.iloc[index]['start']}, ignore_index=True)

    edge_list['edge_idx'] = edge_list.index
    dataset = hv.Table(edge_list)
    return dataset


def create_node_link_dataset2(df):
    # df.values[[np.arange(df.shape[0])] * 2] = 0
    order_list = [(i, i, 0) for i in df.index]
    print(order_list)
    edge_list = df.stack().reset_index()
    edge_list = edge_list[edge_list[0] > 0]
    edge_list.columns = ['start', 'end', 'weight']
    edge_list = edge_list.reset_index()
    edge_list['edge_idx'] = edge_list.index
    dataset = hv.Table(edge_list)
    return dataset, order_list


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
ad_matrix_dataset, ad_matrix_ordering = create_node_link_dataset2(dataframe) #create_ad_matrix_dataset(dataframe)


def modify_doc(doc):
    panel = sidebar.create_sidebar(node_link_dataset, ad_matrix_dataset, dataframe, ad_matrix_ordering)
    return panel.server_doc(doc=doc)


server = Server({'/': modify_doc}, port=5006, allow_websocket_origin=['*'])
server.start()
server.run_until_shutdown()
