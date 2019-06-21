# Author: Jeroen

def getlinks(G):
    nodes = list(G)
    links = {}
    for n in list(G):
        links[n] = set()
    for e in G.edges_iter():
        links[e[0]].add(e[1])
        links[e[1]].add(e[0])
    return links


def bfs(graph, start):
    explored = []
    queue = [start]

    visited = [start]  # to avoid inserting the same node twice into the queue

    # keep looping until there are nodes still to be checked
    while queue:
        # pop shallowest node (first node) from queue
        node = queue.pop(0)
        explored.append(node)
        neighbours = graph[node]

        # add neighbours of node to queue
        for neighbour in neighbours:
            if neighbour not in visited:
                queue.append(neighbour)
                visited.append(neighbour)

    return explored


def definegroups(G):
    groups = {}
    graph = getlinks(G)
    for x in range(len(G)):
        if not graph:
            break
        else:
            groups[x] = set()
            selected = bfs(graph, next(iter(graph)))
            for m in selected:
                groups[x].add(m)
                del graph[m]
    return groups


def groupcolours(G):
    colours = []
    groups = definegroups(G)
