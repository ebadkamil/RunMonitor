"""
Run Visualization software

Author: Ebad Kamil <ebad.kamil@xfel.eu>
All rights reserved.
"""

from .webgui import DashApp


def launch_dash_board():

    app = DashApp()
    app._app.run_server(port=8050, debug=False)
