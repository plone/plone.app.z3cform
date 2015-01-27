# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from lxml import etree
from plone.app.textfield.value import RichTextValue
from plone.app.textfield.widget import RichTextWidget as patextfield_RichTextWidget
from plone.app.widgets.base import InputWidget
from plone.app.widgets.base import SelectWidget as BaseSelectWidget
from plone.app.widgets.base import TextareaWidget
from plone.app.widgets.base import dict_merge
from plone.app.widgets.utils import NotImplemented
from plone.app.widgets.utils import get_ajaxselect_options
from plone.app.widgets.utils import get_date_options
from plone.app.widgets.utils import get_datetime_options
from plone.app.widgets.utils import get_querystring_options
from plone.app.widgets.utils import get_relateditems_options
from plone.app.widgets.utils import get_tinymce_options
from plone.registry.interfaces import IRegistry
from z3c.form.browser.select import SelectWidget as z3cform_SelectWidget
from z3c.form.browser.text import TextWidget as z3cform_TextWidget
from z3c.form.browser.widget import HTMLInputWidget
from z3c.form.interfaces import IAddForm
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import NO_VALUE
from z3c.form.widget import FieldWidget
from z3c.form.widget import Widget
from zope.component import getUtility
from zope.component import ComponentLookupError
from zope.i18n import translate
from zope.interface import implementer
from zope.interface import implementsOnly
from zope.schema.interfaces import IChoice
from zope.schema.interfaces import ICollection
from zope.schema.interfaces import ISequence
from plone.app.widgets.utils import first_weekday

from plone.app.z3cform.converters import (
    DateWidgetConverter, DatetimeWidgetConverter)
from plone.app.z3cform.interfaces import (
    IDatetimeWidget, IDateWidget, IAjaxSelectWidget,
    IRelatedItemsWidget, IQueryStringWidget, IRichTextWidget,
    ISelectWidget)

import json

from Products.CMFPlone.interfaces import IEditingSchema


class BaseWidget(Widget):
    """Base widget for z3c.form."""

    pattern = None
    pattern_options = {}

    def _base(self, pattern, pattern_options={}):
        """Base widget class."""
        raise NotImplemented

    def _base_args(self):
        """Method which will calculate _base class arguments.

        Returns (as python dictionary):
            - `pattern`: pattern name
            - `pattern_options`: pattern options

        :returns: Arguments which will be passed to _base
        :rtype: dict
        """
        if self.pattern is None:
            raise NotImplemented("'pattern' option is not provided.")
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
        return self._base(**self._base_args()).render()


class DateWidget(BaseWidget, HTMLInputWidget):
    """Date widget for z3c.form."""

    _base = InputWidget
    _converter = DateWidgetConverter
    _formater = 'date'

    implementsOnly(IDateWidget)

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
            self._formater, "short")
        if field_value.year > 1900:
            return formatter.format(field_value)

        # due to fantastic datetime.strftime we need this hack
        # for now ctime is default
        return field_value.ctime()


class DatetimeWidget(DateWidget, HTMLInputWidget):
    """Datetime widget for z3c.form.

    :param default_timezone: A Olson DB/pytz timezone identifier or a callback
                             returning such an identifier.
    :type default_timezone: String or callback

    """

    _converter = DatetimeWidgetConverter
    _formater = 'dateTime'

    implementsOnly(IDatetimeWidget)

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
            del args['pattern_options']['time']
        args['pattern_options'] = dict_merge(
            get_datetime_options(self.request),
            args['pattern_options'])

        return args


class SelectWidget(BaseWidget, z3cform_SelectWidget):
    """Select widget for z3c.form."""

    _base = BaseSelectWidget

    implementsOnly(ISelectWidget)

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

        items = []
        for item in self.items():
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


class AjaxSelectWidget(BaseWidget, z3cform_TextWidget):
    """Ajax select widget for z3c.form."""

    _base = InputWidget

    implementsOnly(IAjaxSelectWidget)

    pattern = 'select2'
    pattern_options = BaseWidget.pattern_options.copy()

    separator = ';'
    vocabulary = None
    vocabulary_view = '@@getVocabulary'
    orderable = False

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
        # We need special handling for AddForms
        if IAddForm.providedBy(getattr(self, 'form')):
            context = self.form

        vocabulary_name = self.vocabulary
        field = None
        if IChoice.providedBy(self.field):
            args['pattern_options']['maximumSelectionSize'] = 1
            field = self.field
        elif ICollection.providedBy(self.field):
            field = self.field.value_type
        if not vocabulary_name and field is not None:
            vocabulary_name = field.vocabularyName

        args['pattern_options'] = dict_merge(
            get_ajaxselect_options(context, args['value'], self.separator,
                                   vocabulary_name, self.vocabulary_view,
                                   field_name),
            args['pattern_options'])

        if field and getattr(field, 'vocabulary', None):
            form_url = self.request.getURL()
            source_url = "%s/++widget++%s/@@getSource" % (form_url, self.name)
            args['pattern_options']['vocabularyUrl'] = source_url

        # ISequence represents an orderable collection
        if ISequence.providedBy(self.field) or self.orderable:
            args['pattern_options']['orderable'] = True

        return args


class RelatedItemsWidget(BaseWidget, z3cform_TextWidget):
    """RelatedItems widget for z3c.form."""

    _base = InputWidget

    implementsOnly(IRelatedItemsWidget)

    pattern = 'relateditems'
    pattern_options = BaseWidget.pattern_options.copy()

    separator = ';'
    vocabulary = None
    vocabulary_view = '@@getVocabulary'
    orderable = False

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
        if not vocabulary_name:
            if field is not None and field.vocabularyName:
                vocabulary_name = field.vocabularyName
            else:
                vocabulary_name = 'plone.app.vocabularies.Catalog'

        field_name = self.field and self.field.__name__ or None
        args['pattern_options'] = dict_merge(
            get_relateditems_options(self.context, args['value'],
                                     self.separator, vocabulary_name,
                                     self.vocabulary_view, field_name),
            args['pattern_options'])

        if not self.vocabulary:  # widget vocab takes precedence over field
            if field and getattr(field, 'vocabulary', None):
                form_url = self.request.getURL()
                source_url = "%s/++widget++%s/@@getSource" % (
                    form_url, self.name)
                args['pattern_options']['vocabularyUrl'] = source_url

        return args


class QueryStringWidget(BaseWidget, z3cform_TextWidget):
    """QueryString widget for z3c.form."""

    _base = InputWidget

    implementsOnly(IQueryStringWidget)

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


class RichTextWidget(BaseWidget, patextfield_RichTextWidget):
    """TinyMCE widget for z3c.form."""

    _base = TextareaWidget

    implementsOnly(IRichTextWidget)

    pattern_options = BaseWidget.pattern_options.copy()

    @property
    def pattern(self):
        """dynamically grab the actual pattern name so it will
           work with custom visual editors"""
        registry = getUtility(IRegistry)
        try:
            records = registry.forInterface(IEditingSchema, check=False,
                                            prefix='plone')
            return records.default_editor.lower()
        except AttributeError:
            return 'tinymce'

    def _base_args(self):
        args = super(RichTextWidget, self)._base_args()
        args['name'] = self.name
        properties = getToolByName(self.context, 'portal_properties')
        charset = properties.site_properties.getProperty('default_charset',
                                                         'utf-8')
        value = self.value and self.value.raw_encoded or ''
        args['value'] = (self.request.get(
            self.field.getName(), value)).decode(charset)

        args.setdefault('pattern_options', {})
        merged = dict_merge(get_tinymce_options(self.context, self.field, self.request),  # noqa
                            args['pattern_options'])
        args['pattern_options'] = merged['pattern_options']

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
                mt_pattern_name = '{}{}'.format(
                    self._base._klass_prefix,
                    'textareamimetypeselector'
                )

                # Initialize mimetype selector pattern
                # TODO: default_mime_type returns 'text/html', regardless of
                # settings. fix in plone.app.textfield
                value_mime_type = self.value.mimeType if self.value\
                    else self.field.default_mime_type
                mt_select = etree.Element('select')
                mt_select.attrib['id'] = '{}_text_format'.format(self.id)
                mt_select.attrib['name'] = '{}.mimeType'.format(self.name)
                mt_select.attrib['class'] = mt_pattern_name
                mt_select.attrib['{}{}'.format('data-', mt_pattern_name)] =\
                    json.dumps({
                        'textareaName': self.name,
                        'widgets': {
                            'text/html': {  # TODO: currently, we only support
                                            # richtext widget config for
                                            # 'text/html', no other mimetypes.
                                'pattern': self.pattern,
                                'patternOptions': pattern_options
                            }
                        }
                    })

                # Create a list of allowed mime types
                for mt in allowed_mime_types:
                    opt = etree.Element('option')
                    opt.attrib['value'] = mt
                    if value_mime_type == mt:
                        opt.attrib['selected'] = 'selected'
                    opt.text = mt
                    mt_select.append(opt)

                # Render the combined widget
                rendered = '{}\n{}'.format(
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
