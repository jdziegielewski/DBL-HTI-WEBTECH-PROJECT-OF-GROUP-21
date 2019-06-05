import holoviews as hv
import pandas as pd
import panel as pp
import param
import parambokeh
from bokeh.sampledata import stocks
from bokeh.server.server import Server
from holoviews.operation.timeseries import rolling, rolling_outlier_std
from holoviews.streams import Stream

hv.extension('bokeh', mode='server')

def load_symbol(symbol, variable='adj_close', **kwargs):
    df = pd.DataFrame(getattr(stocks, symbol))
    df['date'] = df.date.astype('datetime64[ns]')
    return hv.Curve(df, ('date', 'Date'), variable)

stock_symbols = ['AAPL', 'IBM', 'FB', 'GOOG', 'MSFT']

class StockExplorer(Stream):
    rolling_window = param.Integer(default=10, bounds=(1, 365))

    symbol = param.ObjectSelector(default='AAPL', objects=stock_symbols)

    def view(self):
        stocks = hv.DynamicMap(load_symbol, kdims=[], streams=[self])

        # Apply rolling mean
        smoothed = rolling(stocks, streams=[self])

        # Find outliers
        outliers = rolling_outlier_std(stocks, streams=[self])
        return smoothed * outliers

def modify_doc(doc):
    explorer = StockExplorer()
    parambokeh.Widgets(explorer, continuous_update=True, callback=explorer.event, on_init=True, mode='server')
    panel = pp.Row(explorer, explorer.view)
    return panel.server_doc(doc=doc)


server = Server({'/': modify_doc}, port=5006, allow_websocket_origin=['*'])
server.start()
server.show('/')
server.run_until_shutdown()