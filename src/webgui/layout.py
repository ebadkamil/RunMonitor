"""
Run Visualization software

Author: Ebad Kamil <ebad.kamil@xfel.eu>
All rights reserved.
"""
import dash_html_components as html
import dash_core_components as dcc
import dash_daq as daq

_run_types = ['raw', 'proc']
_units = ["B", "KB", "MB", "GB", "TB", "PB"]


def get_layout(UPDATE_INT, config=None):

    app_layout = html.Div([

        html.Div([
            dcc.Interval(
                id='interval_component',
                interval=UPDATE_INT * 1000,
                n_intervals=0),
            dcc.Interval(
                id='psutil_component',
                interval=2 * 1000,
                n_intervals=0)], style=dict(textAlign='center')),

        html.Div([
            daq.Gauge(
                id='virtual_memory',
                min=0,
                value=0,
                size=150,
                className="leftbox",
                style=dict(textAlign="center")),
            daq.Gauge(
                id='swap_memory',
                min=0,
                value=0,
                size=150,
                className="rightbox",
                style=dict(textAlign="center")
            ),
        ]),
        daq.LEDDisplay(
            id='timestamp',
            value="1000",
            color="#FF5E5E",
            style=dict(textAlign="center")),

        html.Br(),

        html.Div(
             children=[
                html.Div([

                    html.Div([
                        html.Label("Proposal"),
                        dcc.Input(
                            id='proposal',
                            placeholder="Enter the proposal",
                            type='text',
                            value=config["proposal"]),
                        html.Br(),
                        html.Label("Run Type:",
                            className="leftbox"),
                        dcc.Dropdown(
                            id='run-type',
                            options=[{'label': i, 'value': i}
                                     for i in _run_types],
                            value=_run_types[0],
                            className="rightbox"),

                        html.Hr(),
                        daq.BooleanSwitch(
                            id='start',
                            on=False),
                        html.Br(),
                        html.Div(id="stream-info"),
                        html.Hr(),
                        html.Div(
                            [
                            dcc.Dropdown(
                                id='problem-runs',
                                placeholder="Problematic runs",
                                options=[],
                                className="leftbox"),
                            dcc.Textarea(
                                id="problems-info",
                                placeholder='Validation Message',
                                draggable='false',
                                readOnly=True,
                                disabled=True,
                                style={'width': '100%', 'height': 200})])
                    ],
                    className="pretty_container one-third column"),
                    html.Div(
                        [
                        dcc.Dropdown(
                            id='format-type',
                            options=[{'label': i, 'value': i}
                                     for i in _units],
                            value=_units[0],
                            className="leftbox"),
                        dcc.Graph(
                        id='histogram')],
                        className="two-thirds column")], className="row")]),
        html.Br(),
    ])

    return app_layout
