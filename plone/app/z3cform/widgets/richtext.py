from Acquisition import ImplicitAcquisitionWrapper
from collections import UserDict
from lxml import etree
from plone.app.textfield.value import RichTextValue
from plone.app.textfield.widget import RichTextWidget as patext_RichTextWidget
from plone.app.z3cform.interfaces import IRichTextWidget
from plone.app.z3cform.interfaces import IRichTextWidgetInputModeRenderer
from plone.app.z3cform.utils import closest_content
from plone.app.z3cform.utils import dict_merge
from plone.app.z3cform.widgets.base import BaseWidget
from plone.app.z3cform.widgets.patterns import TextareaWidget
from z3c.form.interfaces import IFieldWidget
from z3c.form.widget import FieldWidget
from zope.component import ComponentLookupError
from zope.component import getMultiAdapter
from zope.component import queryUtility
from zope.interface import implementer
from zope.interface import implementer_only

import json
import logging


logger = logging.getLogger(__name__)


def get_tinymce_options(context, field, request):
    """
    We're just going to be looking up settings from
    plone pattern options
    """
    options = {}
    try:
        pattern_options = getMultiAdapter(
            (context, request, field), name="plone_settings"
        ).tinymce()["data-pat-tinymce"]
        options = json.loads(pattern_options)
    except (ComponentLookupError, AttributeError):
        logger.warning("Can not load tinymce pattern options!", exc_info=True)
    return options


@implementer_only(IRichTextWidget)
class RichTextWidget(BaseWidget, patext_RichTextWidget):
    """TinyMCE widget for z3c.form."""

    _base = TextareaWidget

    pattern_options = BaseWidget.pattern_options.copy()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._pattern = None

    def wrapped_context(self):
        """ "We need to wrap the context to be able to acquire the root
        of the site to get tools, as done in plone.app.textfield"""
        context = self.context
        content = closest_content(context)
        if context.__class__ == dict:
            context = UserDict(self.context)
        return ImplicitAcquisitionWrapper(context, content)

    @property
    def pattern(self):
        """dynamically grab the actual pattern name so it will
        work with custom visual editors"""
        if self._pattern is None:
            self._pattern = self.getWysiwygEditor()
        return self._pattern

    def _base_args(self):
        args = super()._base_args()
        args["name"] = self.name
        value = self.value and self.value.raw or ""
        value = self.request.get(self.name, value)
        args["value"] = value

        args.setdefault("pattern_options", {})
        merged_options = dict_merge(
            get_tinymce_options(
                self.wrapped_context(),
                self.field,
                self.request,
            ),
            args["pattern_options"],
        )
        args["pattern_options"] = merged_options

        return args

    def render(self):
        """Render widget.

        :returns: Widget's HTML.
        :rtype: string
        """
        if self.mode != "display":
            renderer = queryUtility(
                IRichTextWidgetInputModeRenderer,
                name=self.getWysiwygEditor(),
                default=tinymce_richtextwidget_render,
            )
            return renderer(self)

        if not self.value:
            return ""

        if isinstance(self.value, RichTextValue):
            return self.value.output_relative_to(self.context)

        return super().render()

    def render_input_mode(self):
        # MODE "INPUT"
        rendered = ""
        allowed_mime_types = self.allowedMimeTypes()
        if not allowed_mime_types or len(allowed_mime_types) <= 1:
            # Display textarea with default widget
            rendered = super().render()
        else:
            # Let pat-textarea-mimetype-selector choose the widget

            # Initialize the widget without a pattern
            base_args = self._base_args()
            pattern_options = base_args["pattern_options"]
            del base_args["pattern"]
            del base_args["pattern_options"]
            textarea_widget = self._base(None, None, **base_args)
            textarea_widget.klass = "form-control"
            mt_pattern_name = "{}{}".format(
                self._base._klass_prefix,
                "textareamimetypeselector",
            )

            # Initialize mimetype selector pattern
            # TODO: default_mime_type returns 'text/html', regardless of
            # settings. fix in plone.app.textfield
            value_mime_type = (
                self.value.mimeType if self.value else self.field.default_mime_type
            )
            mt_select = etree.Element("select")
            mt_select.attrib["id"] = f"{self.id}_text_format"
            mt_select.attrib["name"] = f"{self.name}.mimeType"
            mt_select.attrib["class"] = f"form-select {mt_pattern_name}"
            mt_select.attrib[f"data-{mt_pattern_name}"] = json.dumps(
                {
                    "textareaName": self.name,
                    "widgets": {
                        "text/html": {  # TODO: currently, we only support
                            # richtext widget config for
                            # 'text/html', no other mimetypes.
                            "pattern": self.pattern,
                            "patternOptions": pattern_options,
                        },
                    },
                },
            )

            # Create a list of allowed mime types
            for mt in allowed_mime_types:
                opt = etree.Element("option")
                opt.attrib["value"] = mt
                if value_mime_type == mt:
                    opt.attrib["selected"] = "selected"
                opt.text = mt
                mt_select.append(opt)

            # Render the combined widget
            rendered = "{}\n{}".format(
                textarea_widget.render(),
                etree.tostring(mt_select, encoding="unicode"),
            )
        return rendered


def tinymce_richtextwidget_render(widget):
    return RichTextWidget.render_input_mode(widget)


@implementer(IFieldWidget)
def RichTextFieldWidget(field, request):
    return FieldWidget(field, RichTextWidget(request))
