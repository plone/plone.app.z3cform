# -*- coding: utf-8 -*-
from Acquisition import ImplicitAcquisitionWrapper
from lxml import etree
from plone.app.textfield.value import RichTextValue
from plone.app.textfield.widget import RichTextWidget as patext_RichTextWidget
from plone.app.widgets.base import dict_merge
from plone.app.widgets.base import InputWidget
from plone.app.widgets.base import SelectWidget as BaseSelectWidget
from plone.app.widgets.base import TextareaWidget
from plone.app.widgets.utils import first_weekday
from plone.app.widgets.utils import get_ajaxselect_options
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
from plone.app.z3cform.interfaces import IQueryStringWidget
from plone.app.z3cform.interfaces import IRelatedItemsWidget
from plone.app.z3cform.interfaces import IRichTextWidget
from plone.app.z3cform.interfaces import ISelectWidget
from plone.app.z3cform.utils import call_callables
from plone.app.z3cform.utils import closest_content
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IEditingSchema
from UserDict import UserDict
from z3c.form.browser.select import SelectWidget as z3cform_SelectWidget
from z3c.form.browser.text import TextWidget as z3cform_TextWidget
from z3c.form.browser.widget import HTMLInputWidget
from z3c.form.interfaces import IEditForm
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import IForm
from z3c.form.interfaces import NO_VALUE
from z3c.form.widget import FieldWidget
from z3c.form.widget import Widget
from zope.component import ComponentLookupError
from zope.component import getUtility
from zope.i18n import translate
from zope.interface import implementer
from zope.interface import implementer_only
from zope.schema.interfaces import IChoice
from zope.schema.interfaces import ICollection
from zope.schema.interfaces import ISequence

import json


class BaseWidget(Widget):
    """Base widget for z3c.form."""

    pattern = None
    pattern_options = {}
    _adapterValueAttributes = (
        Widget._adapterValueAttributes +
        ('pattern_options',)
    )

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
            'pattern': self.pattern,
            'pattern_options': self.pattern_options.copy(),
        }

    def render(self):
        """Render widget.

        :returns: Widget's HTML.
        :rtype: string
        """
        if self.mode != 'input':
            return super(BaseWidget, self).render()

        _base_args = self._base_args()
        _base_args['pattern_options'] = call_callables(
            _base_args['pattern_options'],
            self.context
        )

        pattern_widget = self._base(**_base_args)
        if getattr(self, 'klass', False):
            pattern_widget.klass = u'{0} {1}'.format(
                pattern_widget.klass, self.klass
            )
        return pattern_widget.render()


@implementer_only(IDateWidget)
class DateWidget(BaseWidget, HTMLInputWidget):
    """Date widget for z3c.form."""

    _base = InputWidget
    _converter = DateWidgetConverter
    _formater = 'date'

    pattern = 'pickadate'
    pattern_options = BaseWidget.pattern_options.copy()

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
        args = super(DateWidget, self)._base_args()
        args['name'] = self.name
        args['value'] = (self.request.get(self.name,
                                          self.value) or u'').strip()

        args.setdefault('pattern_options', {})
        args['pattern_options'] = dict_merge(
            get_date_options(self.request),
            args['pattern_options'])

        return args

    def render(self):
        """Render widget.

        :returns: Widget's HTML.
        :rtype: string
        """
        if self.mode != 'display':
            return super(DateWidget, self).render()

        if not self.value:
            return ''

        field_value = self._converter(
            self.field, self).toFieldValue(self.value)
        if field_value is self.field.missing_value:
            return u''

        formatter = self.request.locale.dates.getFormatter(
            self._formater,
            'short'
        )
        if field_value.year > 1900:
            return formatter.format(field_value)

        # due to fantastic datetime.strftime we need this hack
        # for now ctime is default
        return field_value.ctime()


@implementer_only(IDatetimeWidget)
class DatetimeWidget(DateWidget, HTMLInputWidget):
    """Datetime widget for z3c.form.

    :param default_timezone: A Olson DB/pytz timezone identifier or a callback
                             returning such an identifier.
    :type default_timezone: String or callback

    """

    _converter = DatetimeWidgetConverter
    _formater = 'dateTime'

    pattern_options = DateWidget.pattern_options.copy()

    default_timezone = None

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
        args = super(DatetimeWidget, self)._base_args()

        if args['value'] and len(args['value'].split(' ')) == 1:
            args['value'] += ' 00:00'

        args.setdefault('pattern_options', {})
        if 'time' in args['pattern_options']:
            # Time gets set in parent class to false. Remove.
            del args['pattern_options']['time']
        if 'time' in self.pattern_options:
            # Re-apply custom set time options.
            args['pattern_options']['time'] = self.pattern_options['time']
        args['pattern_options'] = dict_merge(
            get_datetime_options(self.request),
            args['pattern_options'])

        return args


@implementer_only(ISelectWidget)
class SelectWidget(BaseWidget, z3cform_SelectWidget):
    """Select widget for z3c.form."""

    _base = BaseSelectWidget

    pattern = 'select2'
    pattern_options = BaseWidget.pattern_options.copy()

    separator = ';'
    noValueToken = u''
    noValueMessage = u''
    multiple = None
    orderable = False
    required = True

    def _base_args(self):
        """Method which will calculate _base class arguments.

        Returns (as python dictionary):
            - `pattern`: pattern name
            - `pattern_options`: pattern options
            - `name`: field name
            - `value`: field value
            - `multiple`: field multiple
            - `items`: field items from which we can select to

        :returns: Arguments which will be passed to _base
        :rtype: dict
        """
        args = super(SelectWidget, self)._base_args()
        args['name'] = self.name
        args['value'] = self.value
        args['multiple'] = self.multiple

        self.required = self.field.required

        options = args.setdefault('pattern_options', {})
        if self.multiple or ICollection.providedBy(self.field):
            options['multiple'] = args['multiple'] = self.multiple = True

        # ISequence represents an orderable collection
        if ISequence.providedBy(self.field) or self.orderable:
            options['orderable'] = True

        if self.multiple:
            options['separator'] = self.separator

        # Allow to clear field value if it is not required
        if not self.required:
            options['allowClear'] = True

        base_items = self.items
        if callable(base_items):
            # items used to be a property in all widgets, then in the select
            # widget it became a method, then in a few others too, but never in
            # all, so this was reverted to let it be a property again.  Let's
            # support both here to avoid breaking on some z3c.form versions.
            # See https://github.com/zopefoundation/z3c.form/issues/44
            base_items = base_items()
        items = []
        for item in base_items:
            if not isinstance(item['content'], basestring):
                item['content'] = translate(
                    item['content'],
                    context=self.request,
                    default=item['value'])
            items.append((item['value'], item['content']))
        args['items'] = items

        return args

    def extract(self, default=NO_VALUE):
        """Override extract to handle delimited response values.
        Skip the vocabulary validation provided in the parent
        method, since it's not ever done for single selects."""
        if (self.name not in self.request and
                self.name + '-empty-marker' in self.request):
            return []
        return self.request.get(self.name, default)


@implementer_only(IAjaxSelectWidget)
class AjaxSelectWidget(BaseWidget, z3cform_TextWidget):
    """Ajax select widget for z3c.form."""

    _base = InputWidget

    pattern = 'select2'
    pattern_options = BaseWidget.pattern_options.copy()

    separator = ';'
    vocabulary = None
    vocabulary_view = '@@getVocabulary'
    orderable = False

    def update(self):
        super(AjaxSelectWidget, self).update()
        field = getattr(self, 'field', None)
        if ICollection.providedBy(self.field):
            field = self.field.value_type
        if (not self.vocabulary and field is not None and
                getattr(field, 'vocabularyName', None)):
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

        args = super(AjaxSelectWidget, self)._base_args()

        args['name'] = self.name
        args['value'] = self.value

        args.setdefault('pattern_options', {})

        field_name = self.field and self.field.__name__ or None

        context = self.context
        view_context = get_widget_form(self)
        # For EditForms and non-Forms (in tests), the vocabulary is looked
        # up on the context, otherwise on the view
        if (
            IEditForm.providedBy(view_context) or
            not IForm.providedBy(view_context)
        ):
            view_context = context

        vocabulary_name = self.vocabulary
        field = None
        if IChoice.providedBy(self.field):
            args['pattern_options']['maximumSelectionSize'] = 1
            field = self.field
        elif ICollection.providedBy(self.field):
            field = self.field.value_type
        if IChoice.providedBy(field):
            args['pattern_options']['allowNewItems'] = 'false'

        args['pattern_options'] = dict_merge(
            get_ajaxselect_options(view_context, args['value'], self.separator,
                                   vocabulary_name, self.vocabulary_view,
                                   field_name),
            args['pattern_options'])

        if field and getattr(field, 'vocabulary', None):
            form_url = self.request.getURL()
            source_url = '{0:s}/++widget++{1:s}/@@getSource'.format(
                form_url,
                self.name
            )
            args['pattern_options']['vocabularyUrl'] = source_url

        # ISequence represents an orderable collection
        if ISequence.providedBy(self.field) or self.orderable:
            args['pattern_options']['orderable'] = True

        if self.vocabulary == 'plone.app.vocabularies.Keywords':
            membership = getToolByName(context, 'portal_membership')
            user = membership.getAuthenticatedMember()

            registry = getUtility(IRegistry)
            roles_allowed_to_add_keywords = registry.get(
                'plone.roles_allowed_to_add_keywords', [])
            roles = set(user.getRolesInContext(context))

            allowNewItems = 'false'
            if roles.intersection(roles_allowed_to_add_keywords):
                allowNewItems = 'true'
            args['pattern_options']['allowNewItems'] = allowNewItems

        return args


@implementer_only(IRelatedItemsWidget)
class RelatedItemsWidget(BaseWidget, z3cform_TextWidget):
    """RelatedItems widget for z3c.form."""

    _base = InputWidget

    pattern = 'relateditems'
    pattern_options = BaseWidget.pattern_options.copy()

    separator = ';'
    vocabulary = None
    vocabulary_override = False
    vocabulary_view = '@@getVocabulary'
    orderable = False

    def update(self):
        super(RelatedItemsWidget, self).update()
        field = getattr(self, 'field', None)
        if ICollection.providedBy(self.field):
            field = self.field.value_type
        if (
            not self.vocabulary and
            field is not None and
            getattr(field, 'vocabularyName', None)
        ):
            self.vocabulary = field.vocabularyName
            self.vocabulary_override = True
        else:
            self.vocabulary = 'plone.app.vocabularies.Catalog'

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
        args = super(RelatedItemsWidget, self)._base_args()

        args['name'] = self.name
        args['value'] = self.value
        args.setdefault('pattern_options', {})

        field = None
        if IChoice.providedBy(self.field):
            args['pattern_options']['maximumSelectionSize'] = 1
            field = self.field
        elif ICollection.providedBy(self.field):
            field = self.field.value_type

        vocabulary_name = self.vocabulary

        field_name = self.field and self.field.__name__ or None

        context = self.context
        view_context = get_widget_form(self)
        # For EditForms and non-Forms (in tests), the vocabulary is looked
        # up on the context, otherwise on the view
        if (
            IEditForm.providedBy(view_context) or
            not IForm.providedBy(view_context)
        ):
            view_context = context

        args['pattern_options'] = dict_merge(
            get_relateditems_options(
                view_context,
                args['value'],
                self.separator,
                vocabulary_name,
                self.vocabulary_view,
                field_name,
            ),
            args['pattern_options']
        )
        if (
            not self.vocabulary_override and
            field and
            getattr(field, 'vocabulary', None)
        ):
            # widget vocab takes precedence over field
            form_url = self.request.getURL()
            source_url = '{0:s}/++widget++{1:s}/@@getSource'.format(
                form_url,
                self.name
            )
            args['pattern_options']['vocabularyUrl'] = source_url

        return args


@implementer_only(IQueryStringWidget)
class QueryStringWidget(BaseWidget, z3cform_TextWidget):
    """QueryString widget for z3c.form."""

    _base = InputWidget

    pattern = 'querystring'
    pattern_options = BaseWidget.pattern_options.copy()

    querystring_view = '@@qsOptions'

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
        args = super(QueryStringWidget, self)._base_args()
        args['name'] = self.name
        args['value'] = self.value

        args.setdefault('pattern_options', {})
        args['pattern_options'] = dict_merge(
            get_querystring_options(self.context, self.querystring_view),
            args['pattern_options'])

        return args


@implementer_only(IRichTextWidget)
class RichTextWidget(BaseWidget, patext_RichTextWidget):
    """TinyMCE widget for z3c.form."""

    _base = TextareaWidget

    pattern_options = BaseWidget.pattern_options.copy()

    def __init__(self, *args, **kwargs):
        super(RichTextWidget, self).__init__(*args, **kwargs)
        self._pattern = None

    def wrapped_context(self):
        """"We need to wrap the context to be able to acquire the root
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
            registry = getUtility(IRegistry)
            try:
                records = registry.forInterface(IEditingSchema, check=False,
                                                prefix='plone')
                default = records.default_editor.lower()
                available = records.available_editors
            except AttributeError:
                default = 'tinymce'
                available = ['TinyMCE']
            tool = getToolByName(self.wrapped_context(), 'portal_membership')
            member = tool.getAuthenticatedMember()
            editor = member.getProperty('wysiwyg_editor')
            if editor in available:
                self._pattern = editor.lower()
            elif editor in ('None', None):
                self._pattern = 'plaintexteditor'
            return default
        return self._pattern

    def _base_args(self):
        args = super(RichTextWidget, self)._base_args()
        args['name'] = self.name
        value = self.value and self.value.raw_encoded or ''
        args['value'] = (self.request.get(
            self.field.getName(), value)).decode('utf-8')

        args.setdefault('pattern_options', {})
        merged_options = dict_merge(
            get_tinymce_options(
                self.context,
                self.field,
                self.request
            ),
            args['pattern_options']
        )
        args['pattern_options'] = merged_options

        return args

    def render(self):
        """Render widget.

        :returns: Widget's HTML.
        :rtype: string
        """
        if self.mode != 'display':
            # MODE "INPUT"
            rendered = ''
            allowed_mime_types = self.allowedMimeTypes()
            if not allowed_mime_types or len(allowed_mime_types) <= 1:
                # Display textarea with default widget
                rendered = super(RichTextWidget, self).render()
            else:
                # Let pat-textarea-mimetype-selector choose the widget

                # Initialize the widget without a pattern
                base_args = self._base_args()
                pattern_options = base_args['pattern_options']
                del base_args['pattern']
                del base_args['pattern_options']
                textarea_widget = self._base(None, None, **base_args)
                textarea_widget.klass = ''
                mt_pattern_name = '{0}{1}'.format(
                    self._base._klass_prefix,
                    'textareamimetypeselector'
                )

                # Initialize mimetype selector pattern
                # TODO: default_mime_type returns 'text/html', regardless of
                # settings. fix in plone.app.textfield
                value_mime_type = self.value.mimeType if self.value\
                    else self.field.default_mime_type
                mt_select = etree.Element('select')
                mt_select.attrib['id'] = '{0}_text_format'.format(self.id)
                mt_select.attrib['name'] = '{0}.mimeType'.format(self.name)
                mt_select.attrib['class'] = mt_pattern_name
                mt_select.attrib[
                    'data-{0}'.format(mt_pattern_name)
                ] = json.dumps(
                    {
                        'textareaName': self.name,
                        'widgets': {
                            'text/html': {  # TODO: currently, we only support
                                            # richtext widget config for
                                            # 'text/html', no other mimetypes.
                                'pattern': self.pattern,
                                'patternOptions': pattern_options
                            }
                        }
                    }
                )

                # Create a list of allowed mime types
                for mt in allowed_mime_types:
                    opt = etree.Element('option')
                    opt.attrib['value'] = mt
                    if value_mime_type == mt:
                        opt.attrib['selected'] = 'selected'
                    opt.text = mt
                    mt_select.append(opt)

                # Render the combined widget
                rendered = '{0}\n{1}'.format(
                    textarea_widget.render(),
                    etree.tostring(mt_select)
                )
            return rendered

        if not self.value:
            return ''

        if isinstance(self.value, RichTextValue):
            return self.value.output

        return super(RichTextWidget, self).render()


@implementer(IFieldWidget)
def DateFieldWidget(field, request):
    widget = FieldWidget(field, DateWidget(request))
    widget.pattern_options.setdefault('date', {})
    try:
        widget.pattern_options['date']['firstDay'] = first_weekday()
    except ComponentLookupError:
        pass
    return widget


@implementer(IFieldWidget)
def DatetimeFieldWidget(field, request):
    return FieldWidget(field, DatetimeWidget(request))


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
