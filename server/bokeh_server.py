import data.examples
import holoviews as hv
from tornado.ioloop import IOLoop
from bokeh.server.server import Server
from visualization.nodelink import shade_network


renderer = hv.renderer('bokeh').instance(mode='server')


def start(app):
    new_server = Server({'/': app}, port=5006, allow_websocket_origin=['localhost:5000'])
    new_server.start()
    new_loop = IOLoop.current()
    new_loop.start()
    return new_server, new_loop


if __name__ == '__main__':
    network = data.examples.load_co_citation()
    dynamic_map = shade_network(network)
    bokeh_app = renderer.app(dynamic_map)
    start(bokeh_app)
