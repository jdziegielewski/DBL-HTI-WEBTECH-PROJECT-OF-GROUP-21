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


def load_local_adm(path):
    df = None
    sep = SEPARATORS.get(filename)

    if sep == "excel":
        df = pd.read_excel(path, engine='xlrd', index_col=0)
    elif sep == "json":
        #df = pd.read_json(path) #read_json doesn't cooperate with the json I have
        with open(path) as jsn:
            jsn_dict = json.load(jsn)
        preserved_order = []
        for people in jsn_dict:
            preserved_order.append(people)
        df = pd.DataFrame.from_dict(jsn_dict, orient='index')
        df = df.reindex(preserved_order)
        print(df)
    else:
        if sep != "":
            df = pd.read_csv(path, sep=sep, engine="c", index_col=0)
        else:
            df = pd.read_csv(path, sep=None, engine="python", index_col=0)#python engine can infer separators to an extent

    if 'Unnamed: 0' in df.columns.values:
        df.columns = np.append(np.delete(df.columns.values, 0), 'NaNs')#dealing with end of line separators (malformed csv)
        df = df.drop('NaNs', axis=1)

    if df.shape != (len(df), len(df)): #if not nxn matrix (wrong format) delete the dataset
        os.remove(path)
        print('BAD DATASET')
        df = pd.read_csv('uploads/Test_data.csv', sep=';', index_col=0)#placeholder, just so it doesnt error

    return df


def create_ad_matrix_dataset(df):
    # df.values[[np.arange(df.shape[0])] * 2] = 0
    edge_list = df.stack().reset_index()
    edge_list.columns = ['start', 'end', 'weight']
    edge_list = edge_list.reset_index()

    edge_list['edge_idx'] = edge_list.index
    dataset = hv.Table(edge_list)
    return dataset


#For saving SEPARATORS
def save_obj(obj, name):
    with open('properties/' + name + '.pkl', 'wb') as file:
        cloudpickle.dump(obj, file)


def load_obj(name):
    with open('properties/' + name + '.pkl', 'rb') as file:
        return cloudpickle.load(file)


SEPARATORS = load_obj("sep")

filename = sys.argv[1]
path = os.path.join("uploads", filename)
dataframe = pd.read_csv(path, sep=';', index_col=0) # supports , ; : in csv and txt

# dataframe = load_local_adm(path)
node_link_dataset = create_node_link_dataset(dataframe)
ad_matrix_dataset = node_link_dataset #create_ad_matrix_dataset(dataframe)


def modify_doc(doc):
    panel = sidebar.create_sidebar(node_link_dataset, ad_matrix_dataset, dataframe)
    return panel.server_doc(doc=doc)


server = Server({'/': modify_doc}, port=5006, allow_websocket_origin=['*'])
server.start()
server.run_until_shutdown()
