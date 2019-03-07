"""Jupyter Notebook Viewer XBlock"""

import logging

import pkg_resources
from webob import Response
from xblock.core import XBlock
from xblock.fields import Integer, Scope, String
from xblock.fragment import Fragment
from xblock.validation import ValidationMessage

from django.http import HttpResponse
from xblockutils.studio_editable import StudioEditableXBlockMixin
from xblockutils.resources import ResourceLoader

from .jupyter_utils import process_nb

log = logging.getLogger(__name__)
LOADER = ResourceLoader(__name__)


class JupyterViewerXBlock(XBlock, StudioEditableXBlockMixin):
    """iframe used with endpoint to render full/section of jupyter notebook"""

    display_name = String(
        display_name="Display Name", default="Jupyter Notebook Viewer",
        scope=Scope.settings,
        help="Name of this XBlock"
    )

    jupyter_url = String(
        help="URL to the .ipynb File",
        scope=Scope.content,
        display_name="Notebook URL",
        default="http://path/to/file.ipynb"
    )

    image_url = String(
        help="(Optional) Absolute URL to images root (http://.../)",
        scope=Scope.content,
        display_name="Image Root URL",
        default=""
    )

    start_tag = String(
        help="(Optional) Finds first occurrence of this text and renders notebook starting in this cell",
        scope=Scope.content,
        display_name="Start Tag",
        default=""
    )

    end_tag = String(
        help="(Optional) Finds first occurrence of this text and renders notebook up to this cell (not inclusive)",
        scope=Scope.content,
        display_name="End Tag",
        default=""
    )

    xblock_height = Integer(
        help="Height of this XBlock (px)",
        scope=Scope.content,
        display_name="Height",
        default=500
    )

    editable_fields = (
        'display_name',
        'jupyter_url',
        'image_url',
        'start_tag',
        'end_tag',
        'xblock_height',
    )


    def validate_field_data(self, validation, data):
        """
        Validate data from edit xblock view.
        """
        def add_error_msg(msg):
            """ Add validation error with the passed error message. """
            validation.add(ValidationMessage(ValidationMessage.ERROR, msg))


        if not data.image_url.endswith('/'):
            add_error_msg(u'Image Root URL must end with a "/" character.')


    def resource_string(self, path):
        """ Handy helper for getting resources from our kit. """
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")


    def student_view(self, context=None):
        """
        Xblock student view.
        """
        context = {
            'iframe_height': self.xblock_height
        }

        frag = Fragment(LOADER.render_template('public/html/student_view.html', context))
        frag.add_javascript_url(
            self.runtime.local_resource_url(self, 'public/js/xblock_jupyter.js')
        )
        frag.initialize_js('initializeIframeSource')

        return frag


    # TO-DO: change this to create the scenarios you'd like to see in the
    # workbench while developing your XBlock.
    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("MyXBlock",
             """<myxblock/>
             """),
            ("Multiple MyXBlock",
             """<vertical_demo>
                <myxblock/>
                <myxblock/>
                <myxblock/>
                </vertical_demo>
             """),
        ]


    @XBlock.handler
    def xblock_handler_jupyter(self, context=None, suffix=''):
        """
        Returns the final Jupyter html view to be embedded inside of iframe tag.
        """
        data = {
            'url': self.jupyter_url,
            'images_url': self.image_url,
            'start': self.start_tag,
            'end': self.end_tag
        }

        try:
            html = process_nb(**data)

        except Exception as exc:  # pylint: disable=broad-except
            log.exception(exc)
            msg = "{} - Check lms/cms logs for more information".format(exc)
            return Response(msg, status=500)

        return Response(body=html, content_type='text/html', charset='utf8')
