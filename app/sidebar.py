import panel as pn


def nodelink_exploration(param):
    return pn.Column(param.layout, width=250)


def admatrix_exploration(param):
    pane = pn.Column(param.layout, width=250)

    dynamic = pn.Column(width=230)
    pane.append(pn.Row(pn.Spacer(width=10), dynamic))

    def callback(*events):
        for event in events:
            if event.name == 'layout':
                dynamic.clear()
                _, params = event.new
                if params is not None:
                    for p in params(param):
                        dynamic.append(p)

    param.watch(callback, ['layout'])
    return pane


def exploration_pane(nodelink_param, admatrix_param):
    return pn.Column('#Explore',
                     nodelink_exploration(nodelink_param),
                     admatrix_exploration(admatrix_param))


def edge_settings(param):
    return pn.Column(param.edge_col,
                     param.edge_alpha,
                     param.esel_col,
                     param.esel_alpha,
                     param.bundle,
                     param.directed,
                     param.rendering_method,
                     width=200)


def node_settings(param):
    return pn.Column(param.node_size,
                     param.node_col,
                     param.line_col,
                     param.node_alpha,
                     param.nsel_col,
                     param.nsel_alpha,
                     width=200)


def matrix_settings(param):
    return pn.Column(param.size,
                     param.marker,
                     param.edge_col,
                     param.alpha,
                     param.nons_alpha,
                     param.esel_col,
                     param.esel_alpha,
                     param.x_axis,
                     param.y_axis,
                     width=200)


def other_settings(nodelink_param, admatrix_param):
    return pn.Column(nodelink_param.toolbar,
                     admatrix_param.toolbar,
                     admatrix_param.x_axis,
                     admatrix_param.y_axis,
                     width=200)


def customization_pane(nodelink_param, admatrix_param):
    return pn.Column('#Customize',
                     pn.Tabs(('Edges', edge_settings(nodelink_param)),
                             ('Nodes', node_settings(nodelink_param)),
                             ('Matrix', matrix_settings(admatrix_param)),
                             ('Other', other_settings(nodelink_param, admatrix_param)),
                             tabs_location='left'), width=250)


def create(nodelink_param, nodelink_view, admatrix_param, admatrix_view):
    panel = pn.Row(pn.Column(exploration_pane(nodelink_param, admatrix_param),
                             customization_pane(nodelink_param, admatrix_param)),
                   nodelink_view,
                   admatrix_view)
    return panel
