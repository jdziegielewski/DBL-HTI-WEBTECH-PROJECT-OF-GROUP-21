import visualization
import data.examples
import networkx as nx
import holoviews as hv
from tornado.ioloop import IOLoop
from bokeh.server.server import Server

renderer = hv.renderer('bokeh').instance(mode='server')


def start(rendered_app):
    new_server = Server({'/': rendered_app, '/upload': }, port=5006, allow_websocket_origin=['localhost:5000'])
    new_server.start()
    new_loop = IOLoop.current()
    new_loop.start()
    return new_server, new_loop


if __name__ == '__main__':
    #network = data.examples.load_co_citation()
    network = nx.karate_club_graph()
    #dynamic_map = shade_network(network)
    dashboard = visualization.create_dashboard(network)
    bokeh_app = renderer.app(dashboard)
    start(bokeh_app)
