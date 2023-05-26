from Acquisition import aq_base
from Acquisition import ImplicitAcquisitionWrapper
from collections import UserDict
from lxml import etree
from OFS.interfaces import ISimpleItem
from plone.app.contentlisting.interfaces import IContentListing
from plone.app.textfield.value import RichTextValue
from plone.app.textfield.widget import RichTextWidget as patext_RichTextWidget
from plone.app.vocabularies.terms import TermWithDescription
from plone.app.widgets.base import dict_merge
from plone.app.widgets.base import InputWidget
from plone.app.widgets.base import SelectWidget as BaseSelectWidget
from plone.app.widgets.base import TextareaWidget
from plone.app.widgets.utils import get_context_url
from plone.app.widgets.utils import get_date_options
from plone.app.widgets.utils import get_datetime_options
from plone.app.widgets.utils import get_querystring_options
from plone.app.widgets.utils import get_relateditems_options
from plone.app.widgets.utils import get_tinymce_options
from plone.app.widgets.utils import get_widget_form
from plone.app.widgets.utils import NotImplemented as PatternNotImplemented
from plone.app.z3cform.converters import DatetimeWidgetConverter
from plone.app.z3cform.converters import DateWidgetConverter
from plone.app.z3cform.interfaces import IAjaxSelectWidget
from plone.app.z3cform.interfaces import IDatetimeWidget
from plone.app.z3cform.interfaces import IDateWidget
from plone.app.z3cform.interfaces import ILinkWidget
from plone.app.z3cform.interfaces import IPloneFormLayer
from plone.app.z3cform.interfaces import IQueryStringWidget
from plone.app.z3cform.interfaces import IRelatedItemsWidget
from plone.app.z3cform.interfaces import IRichTextWidget
from plone.app.z3cform.interfaces import IRichTextWidgetInputModeRenderer
from plone.app.z3cform.interfaces import ISelectWidget
from plone.app.z3cform.interfaces import ISingleCheckBoxBoolWidget
from plone.app.z3cform.interfaces import ITimeWidget
from plone.app.z3cform.utils import call_callables
from plone.app.z3cform.utils import closest_content
from plone.base.utils import safe_text
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from z3c.form import interfaces as form_ifaces
from z3c.form.browser.checkbox import SingleCheckBoxWidget
from z3c.form.browser.select import SelectWidget as z3cform_SelectWidget
from z3c.form.browser.text import TextWidget as z3cform_TextWidget
from z3c.form.interfaces import IEditForm
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import IForm
from z3c.form.interfaces import NO_VALUE
from z3c.form.term import BoolTerms
from z3c.form.term import Terms
from z3c.form.widget import FieldWidget
from z3c.form.widget import Widget
from zope.component import adapter
from zope.component import getUtility
from zope.component import queryUtility
from zope.component.hooks import getSite
from zope.i18n import translate
from zope.interface import implementer
from zope.interface import implementer_only
from zope.schema import interfaces as schema_ifaces
from zope.schema.interfaces import IBool
from zope.schema.interfaces import IChoice
from zope.schema.interfaces import ICollection
from zope.schema.interfaces import ISequence
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

import collections
import json


class BaseWidget(Widget):
    """Base widget for z3c.form."""

    pattern = None
    pattern_options = {}
    _adapterValueAttributes = Widget._adapterValueAttributes + ("pattern_options",)

    def _base(self, pattern, pattern_options={}):
        """Base widget class."""
        raise PatternNotImplemented

    def _base_args(self):
        """Method which will calculate _base class arguments.

        Returns (as python dictionary):
            - `pattern`: pattern name
            - `pattern_options`: pattern options

        :returns: Arguments which will be passed to _base
        :rtype: dict
        """
        if self.pattern is None:
            raise PatternNotImplemented("'pattern' option is not provided.")
        return {
            "pattern": self.pattern,
            "pattern_options": self.pattern_options.copy(),
        }

    def render(self):
        """Render widget.

        :returns: Widget's HTML.
        :rtype: string
        """
        if self.mode != "input":
            return super().render()

        _base_args = self._base_args()
        _base_args["pattern_options"] = call_callables(
            _base_args["pattern_options"],
            self.context,
        )

        pattern_widget = self._base(**_base_args)
        if getattr(self, "klass", False):
            pattern_widget.klass = "{} {}".format(
                pattern_widget.klass,
                self.klass,
            )
        return pattern_widget.render()

    def is_subform_widget(self):
        return getattr(aq_base(self.form), "parentForm", None) is not None


@implementer_only(IDateWidget)
class DateWidget(BaseWidget, z3cform_TextWidget):
    """Date widget for z3c.form.

    :param default_timezone: A Olson DB/pytz timezone identifier or a callback
                             returning such an identifier.
    :type default_timezone: String or callback

    :param default_time: Time used by converter as fallback if no time was set in UI.
    :type default_time: String or callback

    The default_timezone and default_time arguments are only used if a datewidget is
    used on a datetime field. If used on a date field they are ignored.
    """
    _base_type = "date"
    _converter = DateWidgetConverter
    _formater = "date"
    _formater_length = "short"

    default_timezone = None
    default_time = "00:00:00"

    pattern = "date-picker"
    pattern_options = BaseWidget.pattern_options.copy()

    def _base(self, **kw):
        return InputWidget(
            type=self._base_type,
            **kw,
        )

    def _base_args(self):
        """Method which will calculate _base class arguments.

        Returns (as python dictionary):
            - `pattern`: pattern name
            - `pattern_options`: pattern options
            - `name`: field name
            - `value`: field value

        :returns: Arguments which will be passed to _base
        :rtype: dict
        """
        args = super()._base_args()
        args["name"] = self.name
        args["value"] = (self.request.get(self.name, self.value) or "").strip()

        args.setdefault("pattern_options", {})
        if self.field.required:
            # Required fields should not have a "Clear" button
            args["pattern_options"]["clear"] = False
        args["pattern_options"] = dict_merge(
            get_date_options(self.request), args["pattern_options"]
        )

        return args

    def render(self):
        """Render widget.

        :returns: Widget's HTML.
        :rtype: string
        """
        if self.mode != "display":
            self.addClass("form-control")
            return super().render()

        if not self.value:
            return ""

        field_value = self._converter(self.field, self).toFieldValue(self.value)
        if field_value is self.field.missing_value:
            return ""

        formatter = self.request.locale.dates.getFormatter(
            self._formater,
            self._formater_length,
        )
        return formatter.format(field_value)


@implementer_only(IDatetimeWidget)
class DatetimeWidget(DateWidget):
    """Datetime widget for z3c.form.

    :param default_timezone: A Olson DB/pytz timezone identifier or a callback
                             returning such an identifier.
    :type default_timezone: String or callback

    :param default_time: Time used by converter as fallback if no time was set in UI.
    :type default_time: String or callback
    """

    _base_type = "datetime-local"
    _converter = DatetimeWidgetConverter
    _formater = "dateTime"

    default_timezone = None
    default_time = "00:00:00"

    pattern = "datetime-picker"


@implementer_only(ITimeWidget)
class TimeWidget(BaseWidget, z3cform_TextWidget):

    pattern = ""

    def _base(self, **kw):
        return InputWidget(
            type="time",
            name=self.name,
            value=(self.request.get(self.name, self.value) or "").strip(),
            **kw,
        )

    def render(self):
        if self.mode != "display":
            self.addClass("form-control")
        return super().render()


@implementer_only(ISelectWidget)
class SelectWidget(BaseWidget, z3cform_SelectWidget):
    """Select widget for z3c.form."""

    _base = BaseSelectWidget

    pattern = "select2"
    pattern_options = BaseWidget.pattern_options.copy()

    noValueToken = ""
    noValueMessage = ""
    multiple = None
    orderable = False
    required = True

    @property
    def items(self):
        """
        Optionally handle ITreeVocabulary vocabs as dicts.
        """
        terms = self.terms
        if form_ifaces.ITerms.providedBy(terms):
            terms = terms.terms

        base_items = super().items

        if schema_ifaces.ITreeVocabulary.providedBy(terms):
            groups = collections.OrderedDict()
            for group_term, option_terms in terms.items():
                group_widget = type(self)(self.request)
                group_widget.terms = option_terms
                group_label = group_term.title or group_term.value or group_term.token
                groups[group_label] = super(SelectWidget, group_widget).items
            base_items = groups

        def makeItem(item):
            """
            Gather the information needed by the widget for the given term.
            """
            if not isinstance(item["content"], str):
                item["content"] = translate(
                    item["content"], context=self.request, default=item["value"]
                )
            return (item["value"], item["content"])

        if isinstance(base_items, dict):
            items = collections.OrderedDict(
                (group_label, [makeItem(base_item) for base_item in group_options])
                for group_label, group_options in base_items.items()
            )
        else:
            items = [makeItem(item) for item in base_items]

        return items

    def _base_args(self):
        """Method which will calculate _base class arguments.

        Returns (as python dictionary):
            - `pattern`: pattern name
            - `pattern_options`: pattern options
            - `name`: field name
            - `value`: field value
            - `multiple`: field multiple

        :returns: Arguments which will be passed to _base
        :rtype: dict
        """
        args = super()._base_args()
        args["name"] = self.name
        args["value"] = self.value
        args["multiple"] = self.multiple
        if "creators" in self.name:
            breakpoint()
        self.required = self.field.required

        options = args.setdefault("pattern_options", {})
        if self.multiple or ICollection.providedBy(self.field):
            args["multiple"] = self.multiple = True

        # ISequence represents an orderable collection
        if ISequence.providedBy(self.field) or self.orderable:
            options["orderable"] = True

        # Allow to clear field value if it is not required
        if not self.required:
            options["allowClear"] = True

        args["items"] = self.items

        return args

    def extract(self, default=NO_VALUE):
        """Override extract to handle delimited response values.
        Skip the vocabulary validation provided in the parent
        method, since it's not ever done for single selects."""
        if (
            self.name not in self.request
            and self.name + "-empty-marker" in self.request
        ):
            return []
        return self.request.get(self.name, default)


@implementer_only(IAjaxSelectWidget)
class AjaxSelectWidget(SelectWidget, z3cform_SelectWidget):
    """Ajax select widget for z3c.form."""

    vocabulary = None
    vocabulary_view = "@@getVocabulary"
    orderable = False

    def _view_context(self):
        view_context = get_widget_form(self)
        # For EditForms and non-Forms (in tests), the vocabulary is looked
        # up on the context, otherwise on the view
        if IEditForm.providedBy(view_context):
            if self.is_subform_widget():
                view_context = self.form.parentForm.context
            elif not ISimpleItem.providedBy(self.context):
                view_context = self.form.context
            else:
                view_context = self.context
        elif not IForm.providedBy(view_context):
            view_context = self.context
        return view_context

    def get_vocabulary(self):
        if self.vocabulary and isinstance(self.vocabulary, str):
            factory = queryUtility(
                IVocabularyFactory,
                self.vocabulary,
            )
            if factory:
                return factory(self._view_context())
        return self.vocabulary

    def display_items(self):
        if self.value:
            tokens = self.value
            vocabulary = self.get_vocabulary()
            for token in tokens:
                item = {"token": token, "title": token}
                if vocabulary is not None:
                    try:
                        item["title"] = vocabulary.getTermByToken(token).title
                    except LookupError:
                        pass
                yield item

    def _ajaxselect_options(self):
        options = {}
        if self.vocabulary:
            options["vocabularyUrl"] = "{}/{}?name={}".format(
                get_context_url(self._view_context()),
                self.vocabulary_view,
                self.vocabulary,
            )
            field_name = self.field and self.field.__name__ or None
            if field_name:
                options["vocabularyUrl"] += f"&field={field_name}"
        return options

    def update(self):
        super().update()
        field = getattr(self, "field", None)
        field = getattr(field, "value_type", field)
        if (
            not self.vocabulary
            and field is not None
            and getattr(field, "vocabularyName", None)
        ):
            self.vocabulary = field.vocabularyName

    def _base_args(self):
        """Method which will calculate _base class arguments.

        Returns (as python dictionary):
            - `pattern`: pattern name
            - `pattern_options`: pattern options
            - `name`: field name
            - `value`: field value

        :returns: Arguments which will be passed to _base
        :rtype: dict
        """
        args = super()._base_args()
        args["name"] = self.name
        args["value"] = self.value
        args.setdefault("pattern_options", {})
        context = self.context
        field = None

        if IChoice.providedBy(self.field):
            args["pattern_options"]["maximumSelectionSize"] = 1
            field = self.field
        elif ICollection.providedBy(self.field):
            field = self.field.value_type
        if IChoice.providedBy(field):
            args["pattern_options"]["allowNewItems"] = "false"

        args["pattern_options"] = dict_merge(
            self._ajaxselect_options(), args["pattern_options"]
        )

        if field and getattr(field, "vocabulary", None):
            form_url = self.request.getURL()
            source_url = "{:s}/++widget++{:s}/@@getSource".format(
                form_url,
                self.name,
            )
            args["pattern_options"]["vocabularyUrl"] = source_url

        # ISequence represents an orderable collection
        if ISequence.providedBy(self.field) or self.orderable:
            args["pattern_options"]["orderable"] = True

        if self.vocabulary == "plone.app.vocabularies.Keywords":
            membership = getToolByName(context, "portal_membership")
            user = membership.getAuthenticatedMember()

            registry = getUtility(IRegistry)
            roles_allowed_to_add_keywords = registry.get(
                "plone.roles_allowed_to_add_keywords", set()
            )
            roles = set(user.getRolesInContext(context))
            allowNewItems = bool(
                roles.intersection(roles_allowed_to_add_keywords),
            )
            args["pattern_options"]["allowNewItems"] = str(
                allowNewItems,
            ).lower()

        args["items"] = self.items

        return args


@implementer_only(IRelatedItemsWidget)
class RelatedItemsWidget(BaseWidget, z3cform_TextWidget):
    """RelatedItems widget for z3c.form."""

    _base = InputWidget

    pattern = "relateditems"
    pattern_options = BaseWidget.pattern_options.copy()

    separator = ";"
    vocabulary = None
    vocabulary_override = False
    vocabulary_view = "@@getVocabulary"
    orderable = False

    def update(self):
        super().update()
        field = getattr(self, "field", None)
        if ICollection.providedBy(self.field):
            field = self.field.value_type
        if (
            not self.vocabulary
            and field is not None
            and getattr(field, "vocabularyName", None)
        ):
            self.vocabulary = field.vocabularyName
            self.vocabulary_override = True
        else:
            self.vocabulary = "plone.app.vocabularies.Catalog"

    def _base_args(self):
        """Method which will calculate _base class arguments.

        Returns (as python dictionary):
            - `pattern`: pattern name
            - `pattern_options`: pattern options
            - `name`: field name
            - `value`: field value

        :returns: Arguments which will be passed to _base
        :rtype: dict
        """
        args = super()._base_args()

        args["name"] = self.name
        args["value"] = self.value
        args.setdefault("pattern_options", {})

        field = None
        if IChoice.providedBy(self.field):
            args["pattern_options"]["maximumSelectionSize"] = 1
            field = self.field
        elif ICollection.providedBy(self.field):
            field = self.field.value_type

        vocabulary_name = self.vocabulary

        field_name = self.field and self.field.__name__ or None

        context = self.context
        view_context = get_widget_form(self)
        # For EditForms and non-Forms (in tests), the vocabulary is looked
        # up on the context, otherwise on the view
        if IEditForm.providedBy(view_context):
            if self.is_subform_widget():
                view_context = self.form.parentForm.context
            elif not ISimpleItem.providedBy(context):
                view_context = self.form.context
            else:
                view_context = context
        elif not IForm.providedBy(view_context):
            view_context = context
        else:
            pass
            # view_context is defined above already

        root_search_mode = (
            args["pattern_options"].get("mode", None)
            and "basePath" not in args["pattern_options"]
        )

        args["pattern_options"] = dict_merge(
            get_relateditems_options(
                view_context,
                args["value"],
                self.separator,
                vocabulary_name,
                self.vocabulary_view,
                field_name,
            ),
            args["pattern_options"],
        )
        if root_search_mode:
            # Delete default basePath option in search mode, when no basePath
            # was explicitly set.
            del args["pattern_options"]["basePath"]
        if (
            not self.vocabulary_override
            and field
            and getattr(field, "vocabulary", None)
        ):
            # widget vocab takes precedence over field
            form_url = self.request.getURL()
            source_url = "{:s}/++widget++{:s}/@@getSource".format(
                form_url,
                self.name,
            )
            args["pattern_options"]["vocabularyUrl"] = source_url

        return args

    def items(self):
        """Return item for the widget values for the display template

        Query the catalog for the widget-value (uuids) to only display items
        that the user is allowed to see. Accessing the value with e.g.
        getattr(self.context, self.__name__) would yield the items unfiltered.
        Uses IContentListing for easy access to MimeTypeIcon and more.
        """
        results = []
        if not self.value:
            return results
        separator = getattr(self, "separator", ";")
        uuids = self.value.split(separator)

        try:
            catalog = getToolByName(self.context, "portal_catalog")
        except AttributeError:
            catalog = getToolByName(getSite(), "portal_catalog")

        brains = catalog(UID=uuids)
        # restore original order
        results = sorted(brains, key=lambda brain: uuids.index(brain.UID))
        return IContentListing(results)


@implementer_only(IQueryStringWidget)
class QueryStringWidget(BaseWidget, z3cform_TextWidget):
    """QueryString widget for z3c.form."""

    _base = InputWidget

    pattern = "querystring"
    pattern_options = BaseWidget.pattern_options.copy()

    querystring_view = "@@qsOptions"

    def _base_args(self):
        """Method which will calculate _base class arguments.

        Returns (as python dictionary):
            - `pattern`: pattern name
            - `pattern_options`: pattern options
            - `name`: field name
            - `value`: field value

        :returns: Arguments which will be passed to _base
        :rtype: dict
        """
        args = super()._base_args()
        args["name"] = self.name
        args["value"] = self.value

        args.setdefault("pattern_options", {})
        args["pattern_options"] = dict_merge(
            get_querystring_options(self.context, self.querystring_view),
            args["pattern_options"],
        )

        return args


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
            mt_select.attrib["class"] = "form-select {}".format(mt_pattern_name)
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


@implementer_only(ILinkWidget)
class LinkWidget(z3cform_TextWidget):
    """Implementation of enhanced link widget.

    .. note::
        Unlike the others here, this is not a plone.app.widgets based widget
        and it uses it's own template.
    """

    def pattern_data(self):
        pattern_data = {
            "vocabularyUrl": "{}/@@getVocabulary?name=plone.app.vocabularies.Catalog".format(  # noqa
                getSite().absolute_url(0),
            ),
            "maximumSelectionSize": 1,
        }
        return json.dumps(pattern_data)

    def extract(self, default=NO_VALUE):
        form = self.request.form
        internal = form.get(self.name + ".internal")
        external = form.get(self.name + ".external")
        email = form.get(self.name + ".email")
        if internal:
            url = "${portal_url}/resolveuid/" + internal
        elif email:
            subject = form.get(self.name + ".subject")
            if email[:7] != "mailto:":
                email = "mailto:" + email
            if not subject:
                url = email
            else:
                url = "{email}?subject={subject}".format(
                    email=email,
                    subject=subject,
                )
        else:
            url = external  # the default is `http://` so we land here
        if url:
            self.request.form[self.name] = safe_text(url)
        return super().extract(default=default)


@implementer(IFieldWidget)
def DateFieldWidget(field, request):
    return FieldWidget(field, DateWidget(request))


@implementer(IFieldWidget)
def DatetimeFieldWidget(field, request):
    return FieldWidget(field, DatetimeWidget(request))


@implementer(IFieldWidget)
def TimeFieldWidget(field, request):
    return FieldWidget(field, TimeWidget(request))


@implementer(IFieldWidget)
def SelectFieldWidget(field, request):
    return FieldWidget(field, SelectWidget(request))


@implementer(IFieldWidget)
def AjaxSelectFieldWidget(field, request, extra=None):
    if extra is not None:
        request = extra
    return FieldWidget(field, AjaxSelectWidget(request))


@implementer(IFieldWidget)
def RelatedItemsFieldWidget(field, request, extra=None):
    if extra is not None:
        request = extra
    return FieldWidget(field, RelatedItemsWidget(request))


@implementer(IFieldWidget)
def RichTextFieldWidget(field, request):
    return FieldWidget(field, RichTextWidget(request))


@implementer(IFieldWidget)
def QueryStringFieldWidget(field, request, extra=None):
    if extra is not None:
        request = extra
    return FieldWidget(field, QueryStringWidget(request))


@implementer(IFieldWidget)
def LinkFieldWidget(field, request):
    return FieldWidget(field, LinkWidget(request))


@implementer_only(ISingleCheckBoxBoolWidget)
class SingleCheckBoxBoolWidget(SingleCheckBoxWidget):
    """Single Input type checkbox widget implementation."""

    klass = "single-checkbox-bool-widget"

    @property
    def label(self):
        if self.mode == "input":
            return ""
        return getattr(self, "_label", "")

    @label.setter
    def label(self, value):
        self._label = value

    @property
    def description(self):
        if self.mode == "input":
            return ""
        return getattr(self, "_description", "")

    @description.setter
    def description(self, value):
        self._description = value

    def updateTerms(self):
        if self.mode == "input":
            # in input mode use only one checkbox with true
            self.terms = Terms()
            self.terms.terms = SimpleVocabulary(
                (
                    TermWithDescription(
                        True,
                        "selected",
                        getattr(self, "_label", None) or self.field.title,
                        getattr(
                            self,
                            "_description",
                            None,
                        )
                        or self.field.description,
                    ),
                )
            )
            return self.terms
        if not self.terms:
            self.terms = Terms()
            self.terms.terms = SimpleVocabulary(
                [
                    SimpleTerm(*args)
                    for args in [
                        (True, "selected", BoolTerms.trueLabel),
                        (False, "unselected", BoolTerms.falseLabel),
                    ]
                ],
            )
        return self.terms

    @property
    def items(self):
        result = super().items
        for record in result:
            term = self.terms.terms.getTermByToken(record["value"])
            record["description"] = getattr(term, "description", "")
            record["required"] = self.required
        return result


@adapter(IBool, IPloneFormLayer)
@implementer(IFieldWidget)
def SingleCheckBoxBoolFieldWidget(field, request):
    """IFieldWidget factory for CheckBoxWidget."""
    return FieldWidget(field, SingleCheckBoxBoolWidget(request))
