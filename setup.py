import os.path as osp
import re
import sys
from setuptools import setup, find_packages


def find_version():
    with open(osp.join('src', '__init__.py'), 'r') as f:
        match = re.search(r'^__version__ = "(\d+\.\d+\.\d+)"', f.read(), re.M)
        if match is not None:
            return match.group(1)
        raise RuntimeError("Unable to find version string.")


setup(name="dashboard",
      version=find_version(),
      author="Ebad Kamil",
      author_email="kamilebad@gmail.com",
      maintainer="Ebad Kamil",
      packages=find_packages(),
      entry_points={
          "console_scripts": [
              "launch_dash_board = src.application:launch_dash_board"
          ],
      },
      install_requires=[
           'dash>=1.6.1',
           'dash-daq>=0.3.1',
           'psutil',
           'numpy'
      ],
      extras_require={
        'test': [
          'pytest',
        ]
      },
      python_requires='>=3.6',
)
