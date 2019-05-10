import os
import pandas as pd
import networkx as nx


def load_local(self, sep=';', clean=True):
    dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(dir, self)
    df = pd.read_csv(path, sep=sep)
    if clean:
        df = df.loc[:, df.columns[1:]]
    dg = nx.DiGraph(df.values)
    return df, dg


def load_similarity():
    return load_local("GephiMatrix_author_similarity.csv")


def load_co_authorship():
    return load_local("GephiMatrix_co-authorship.csv")


def load_co_citation():
    return load_local("GephiMatrix_co-citation.csv")