import networkx as nx

groups = [[], []]


def initGraph(G):
    adjList(G)
    groupNodes(G)


def groupNodes(G):
    nodes = G.nodes


def adjList(G):
    for n in G.nodes:
        for e in G.edges_iter():
            groups[e[0]].append(e[1])
