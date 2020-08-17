"""
Run Visualization software

Author: Ebad Kamil <ebad.kamil@xfel.eu>
All rights reserved.
"""

import argparse
import os
import sys
import time

import psutil

from .webgui import DashApp


def launch_dash_board():

    app = DashApp()
    app._app.run_server(debug=False)
