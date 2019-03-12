"""Setup for jupyter-viewer-xblock XBlock."""

import os
import re
from setuptools import setup


def package_data(pkg, roots):
    """Generic function to find package_data.

    All of the files under each of the `roots` will be declared as package
    data for package `pkg`.

    """
    data = []
    for root in roots:
        for dirname, _, files in os.walk(os.path.join(pkg, root)):
            for fname in files:
                data.append(os.path.relpath(os.path.join(dirname, fname), pkg))

    return {pkg: data}


def get_version():
    """
    Retrives the version string from: xblock_jupyter_viewer/__init__.py.
    """
    file_path = os.path.join('xblock_jupyter_viewer', '__init__.py')
    initfile_lines = open(file_path, 'rt').readlines()
    version_regex = r"^__version__ = ['\"]([^'\"]*)['\"]"
    for line in initfile_lines:
        match_string = re.search(version_regex, line, re.M)
        if match_string:
            return match_string.group(1)
    raise RuntimeError('Unable to find version string in %s.' % (file_path,))


setup(
    name='xblock_jupyter_viewer',
    version=get_version(),
    description='View Jupyter Notebooks in your XBlock',
    license='UNKNOWN',          # TODO: choose a license: 'AGPL v3' and 'Apache 2.0' are popular.
    packages=[
        'xblock_jupyter_viewer',
    ],
    install_requires=[
        'XBlock',
        'nbconvert',
        'nbformat',
        'requests',
        'Jinja2==2.10'
    ],
    entry_points={
        'xblock.v1': [
            'xblock_jupyter_viewer = xblock_jupyter_viewer:JupyterViewerXBlock',
        ]
    },
    package_data=package_data("xblock_jupyter_viewer", ["static", "public", "templates"]),
)
