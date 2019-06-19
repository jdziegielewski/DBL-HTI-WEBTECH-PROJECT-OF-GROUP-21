import colorcet
from collections import OrderedDict

tools = ['box_select', 'hover', 'tap']

cmaps = OrderedDict([('Colorcet -- Fire', colorcet.fire),
                     ('Colorcet -- BMY', colorcet.bmy),
                     ('Colorcet -- BMW', colorcet.bmy),
                     ('Colorcet -- BGY', colorcet.bgy),
                     ('Gradient -- Blue-Magenta-Yellow', ['blue', 'magenta', 'yellow']),
                     ('Solid -- Yellow', ['yellow']),
                     ('Solid -- Blue', ['blue']),
                     ('Solid -- Purple', ['purple']),
                     ('Solid -- Green', ['green']),
                     ('Solid -- Red', ['red']),
                     ('Solid -- White', ['white'])])


def disable_logo(plot, element):
    plot.state.toolbar.logo = None
