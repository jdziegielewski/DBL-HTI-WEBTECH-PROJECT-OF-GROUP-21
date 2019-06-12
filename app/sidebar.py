import panel as pn
from nodelink import NodeLink
from admatrix import AdMatrix


def create_sidebar(node_link_dataset, ad_matrix_dataset, dataframe):
    nodelink = NodeLink(node_link_dataset)
    admatrix = AdMatrix(ad_matrix_dataset, dataframe)
    nodelink.link_admatrix(admatrix)
    admatrix.link_nodelink(nodelink)
    nodelink_view = nodelink.view
    admatrix_view = admatrix.start

    exploration = pn.Column('#Explore',
                            nodelink.param.layout,
                            admatrix.param.layout, width=250)

    edge_settings = pn.Column(nodelink.param.edge_col,
                              nodelink.param.edge_alpha,
                              nodelink.param.esel_col,
                              nodelink.param.esel_alpha,
                              nodelink.param.bundle,
                              nodelink.param.rendering_method, width=200)

    node_settings = pn.Column(nodelink.param.node_size,
                              nodelink.param.node_col,
                              nodelink.param.line_col,
                              nodelink.param.node_alpha,
                              nodelink.param.nsel_col,
                              nodelink.param.nsel_alpha, width=200)

    matrix_settings = pn.Column(admatrix.param.size,
                                admatrix.param.marker,
                                admatrix.param.edge_col,
                                admatrix.param.alpha,
                                admatrix.param.nons_alpha,
                                admatrix.param.esel_col,
                                admatrix.param.esel_alpha, width=200)

    customization_tabs = pn.Tabs(('Edges', edge_settings),
                                 ('Nodes', node_settings),
                                 ('Matrix', matrix_settings),
                                 tabs_location='left')

    customization = pn.Column('#Customize',
                              customization_tabs, width=250)

    sidebar = pn.Column(exploration, customization)

    panel = pn.Row(sidebar, nodelink_view, admatrix_view)
    return panel


    #col1 = pn.Row(pn.Param(nodelink.param, widgets={'rendering_method': pn.widgets.RadioButtonGroup}),  height=100, background='#f0f0f0')

    # gspec = pn.GridSpec(sizing_mode='stretch_both')
    # gspec[0, :5] = tabs
    # gspec[1:5, :5] = main_row

    # panel = main_row  pn.Column(col1, main_row) #pn.Column(, main_row)

    #slider = pn.widgets.FloatSlider(name='Test Slider', start=0, end=10, step=0.2, value=3)
    #slider.param.watch(admatrix.test_trigger, 'value')
    #slider.param.trigger('value')

    #toggle = pn.widgets.Toggle(name='Datashade', button_type='primary', value=False)
    #toggle.param.watch(nodelink.callback, 'value')

    #c.append(pn.pane.Markdown(object='Layout'))
    #nodelink.addd(c)
