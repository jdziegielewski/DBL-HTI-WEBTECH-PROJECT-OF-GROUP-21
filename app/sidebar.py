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
                     admatrix_exploration(admatrix_param),
                     width=250)


def edge_settings(param):
    dynamic = pn.Column(param.edge_alpha, width=200)
    pane = pn.Column(param.rendering_method,
                     param.edge_col,
                     dynamic,
                     param.nsel_col,
                     param.nsel_alpha,
                     param.bundle,
                     width=200)

    def callback(*events):
        for event in events:
            if event.name == 'rendering_method':
                dynamic.clear()
                if event.new != 0:
                    dynamic.append(param.edge_alpha)

    param.watch(callback, ['rendering_method'])
    return pane


def node_settings(param):
    return pn.Column(param.node_size,
                     param.node_col,
                     param.line_col,
                     param.node_alpha,
                     width=200)


def matrix_settings(param):
    return pn.Column(param.size,
                     param.edge_col,
                     param.marker,
                     param.alpha,
                     param.nons_alpha,
                     width=200)


def interaction_settings(nodelink_param, admatrix_param):
    return pn.Column(nodelink_param.esel_col,
                     nodelink_param.esel_alpha,
                     admatrix_param.esel_col,
                     admatrix_param.esel_alpha,
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
                             ('Links', interaction_settings(nodelink_param, admatrix_param)),
                             ('Other', other_settings(nodelink_param, admatrix_param)),
                             tabs_location='left'), width=250)


def info_pane(nodelink_param, admatrix_param):
    jobs = pn.Column(pn.widgets.StaticText(value='aaa'))
    return pn.Column('Info', jobs)


def create(nodelink_param, nodelink_view, admatrix_param, admatrix_view):
    panel = pn.Row(pn.Column(exploration_pane(nodelink_param, admatrix_param),
                             customization_pane(nodelink_param, admatrix_param),
                             info_pane(nodelink_param, admatrix_param),
                             width=250),
                   nodelink_view,
                   admatrix_view)
    return panel
