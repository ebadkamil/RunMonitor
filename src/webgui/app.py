"""
Run Visualization software

Author: Ebad Kamil <ebad.kamil@xfel.eu>
All rights reserved.
"""
from math import ceil
from multiprocessing import Queue
import queue

import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go

import psutil as ps

from .layout import get_layout
from .config import config
from ..file_checker import RunServer
from ..helpers import find_proposal, get_size_format


def get_virtual_memory():
    virtual_memory, swap_memory = ps.virtual_memory(), ps.swap_memory()
    return virtual_memory, swap_memory


class DashApp:

    def __init__(self):
        app = dash.Dash(__name__)
        app.config['suppress_callback_exceptions'] = True
        self._app = app
        self._config = config
        self._data_queue = Queue(maxsize=1)
        self._run_server = None
        self._data = None
        self.setLayout()
        self.register_callbacks()

    def setLayout(self):
        self._app.layout = get_layout(config["TIME_OUT"], self._config)

    def register_callbacks(self):
        """Register callbacks"""
        @self._app.callback(
            Output('timestamp', 'value'),
            [Input('interval_component', 'n_intervals')])
        def update_timestamp(n):
            self._update()
            if self._data is None:
                raise dash.exceptions.PreventUpdate
            return str(self._data.timestamp)

        @self._app.callback(
            [Output('virtual_memory', 'value'),
             Output('virtual_memory', 'max'),
             Output('swap_memory', 'value'),
             Output('swap_memory', 'max')],
            [Input('psutil_component', 'n_intervals')])
        def update_memory_info(n):
            try:
                virtual, swap = get_virtual_memory()
            except Exception:
                raise dash.exceptions.PreventUpdate
            return ((virtual.used/1024**3), ceil((virtual.total/1024**3)),
                    (swap.used/1024**3), ceil((swap.total/1024**3)))

        @self._app.callback(
            Output('stream-info', 'children'),
            [Input('start', 'on')],
            [State('proposal', 'value'),
             State('run-type', 'value')])
        def start_run_server(state, proposal, run_type):
            info = ""
            if state:
                if not (proposal and run_type):
                    info = f"Either Folder or port number missing"
                    return [info]
                proposal = find_proposal(proposal, data=run_type)
                self._run_server = RunServer(proposal, self._data_queue)
                try:
                    print("Start ", self._run_server)
                    self._run_server.start()
                    info = f"Checking Files of type {run_type} in {proposal}"
                except Exception as ex:
                    info = repr(ex)
            elif not state:
                if self._run_server is not None and self._run_server.is_alive():
                    info = "Shutdown Run Server"
                    self._run_server.terminate()
                if self._run_server is not None:
                    self._run_server.join()

            return [info]

        @self._app.callback(Output('histogram', 'figure'),
                            [Input('timestamp', 'value'),
                             Input('format-type', 'value')])
        def update_histogram_figure(timestamp, format):
            if self._data is None or self._data.timestamp != timestamp or self._data.size_info is None:
                raise dash.exceptions.PreventUpdate

            size_info = self._data.size_info
            runs = list(size_info.keys())
            sizes = [get_size_format(size, unit=format)
                     for size in list(size_info.values())]
            traces = [go.Bar(
                x=runs, y=sizes,
                marker_color='crimson',
                )]
            figure = {
                'data': traces,
                'layout': go.Layout(
                    margin={'l': 40, 'b': 40, 't': 40, 'r': 10},
                    xaxis={'title':'Runs'},
                    yaxis={'title':f"Size ({format})"}
                )
            }

            return figure

    def _update(self):
        try:
            self._data = self._data_queue.get_nowait()
        except queue.Empty:
            pass