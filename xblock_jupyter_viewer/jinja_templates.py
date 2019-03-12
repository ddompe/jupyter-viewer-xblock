"""
Loader module for Jinja templates.
"""
from jinja2 import PackageLoader


def get_package_loader():
    """
    Function to get the package loader for this Xblock app.
    """
    loader = PackageLoader('xblock_jupyter_viewer', 'templates')

    return loader
