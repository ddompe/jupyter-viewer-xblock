import json
import logging

import pkg_resources
import requests

import nbformat
from nbconvert import HTMLExporter

from .jinja_templates import get_package_loader
from .post_processors import insert_target_blank, remove_box_shadow
from .preprocessors import ImageReplacement, RemoveCustomCSS

log = logging.getLogger(__name__)


def fetch_notebook(url):
    """ Fetches the notebook from URL. """

    log.info("Fetching URL: {}".format(url))
    response = requests.get(url)
    return response


def json_to_nb_format(nb_str):
    """
    Converts Jupyter Notebook JSON to Notebook node format.

    Notebook format more info: https://nbformat.readthedocs.io/en/latest/
    """

    notebook_node = nbformat.reads(nb_str, as_version=4)
    return notebook_node


def convert_to_html(notebook):
    """
    Converts from notebook dict to HTML template.

    More info: https://nbconvert.readthedocs.io/en/latest/nbconvert_library.html
    """

    loader = get_package_loader()
    # Get the default Jupyter notebook css, cause, the original returned by resources['inlining']['css'][0],
    # contains a path to a css.map file, that doesn't exists in this context and error in raised.
    # Original css file comes from: https://github.com/jupyter/notebook/blob/master/notebook/static/style/style.less
    notebook_default_css = resource_string('/public/css/jupyter-notebook.min.css')

    # If template_file is not set, loads full.tpl template file by default.
    exporter = HTMLExporter(extra_loaders=[loader])
    body, resources = exporter.from_notebook_node(
        notebook,
        resources={
            "notebook_default_css": notebook_default_css
        }
    )

    return body, resources


def filter_start_end(nb, start_tag=None, end_tag=None):
    """Filter out everything outside of `start_tag` and `end_tag`"""

    # Just return if nothing to filter
    if start_tag is None and end_tag is None:
        return nb

    start_cell_num = 0
    num_cells = end_cell_num = len(nb['cells'])
    for cell_num, cell in enumerate(nb['cells']):
        # Find first occurrence of start_tag
        if start_tag and start_tag in cell['source'] and start_cell_num == 0:
            start_cell_num = cell_num
        # Find first occurrence of end_tag
        if end_tag and end_tag in cell['source'] and end_cell_num == num_cells:
            end_cell_num = cell_num

    if start_tag and start_cell_num == 0:
        log.warning("No cell with start content: {} found".format(start_tag))
    if end_tag and end_cell_num == num_cells:
        log.warning("No cell with start content: {} found".format(end_tag))

    nb['cells'] = nb['cells'][start_cell_num:end_cell_num]

    return nb


def preprocess(nb, processors):
    """Applies preprocessor to each cell"""
    gen = (cell for cell in nb['cells'])

    # Run processor on each cell
    for cell in gen:
        for t in processors:
            t.process_cell(cell)

    # Run finish on each processor
    for t in processors:
        t.finish()


def postprocess(raw_html):
    """Post-processes raw html"""
    html = remove_box_shadow(raw_html)
    html = insert_target_blank(html)
    return html


def process_nb(url, images_url=None, start=None, end=None):
    """Main method to fetch, process, and return HTML for ipython notebook"""

    # Retrieve nb from URL, conver to python fmt, and filter appropriately
    response = fetch_notebook(url)
    nb = json_to_nb_format(response.text)
    nb = filter_start_end(nb, start, end)

    # Setup pre-processors
    transforms = [RemoveCustomCSS(nb)]
    if images_url:
        transforms.append(ImageReplacement(nb, images_url))

    # Run transformation pipeline
    preprocess(nb, transforms)
    html, resources = convert_to_html(nb)
    html = postprocess(html)

    return html


def resource_string(path):
    """ Handy helper for getting resources from our kit. """
    data = pkg_resources.resource_string(__name__, path)
    return data.decode("utf8")
