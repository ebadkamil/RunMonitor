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
    parser = argparse.ArgumentParser(prog="Run Monitor")
    parser.add_argument("--validate", action='store_true',
                        help="To enable run validation")

    args = parser.parse_args()

    app = DashApp(validate=args.validate)
    app._app.run_server(port=8050, debug=False)
