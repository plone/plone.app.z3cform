# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser import BrowserView
from ZPublisher.Iterators import filestream_iterator
from os.path import basename
from os.path import join
from lxml import etree
from plone.app.textfield.value import RichTextValue
from plone.app.textfield.widget import RichTextWidget as patextfield_RichTextWidget
from plone.app.widgets.base import InputWidget
from plone.app.widgets.base import SelectWidget as BaseSelectWidget
from plone.app.widgets.base import TextareaWidget
from plone.app.widgets.base import DivWidget
from plone.app.widgets.base import dict_merge
from plone.app.widgets.utils import NotImplemented
from plone.app.widgets.utils import get_ajaxselect_options
from plone.app.widgets.utils import get_date_options
from plone.app.widgets.utils import get_datetime_options
from plone.app.widgets.utils import get_querystring_options
from plone.app.widgets.utils import get_relateditems_options
from plone.app.widgets.utils import get_tinymce_options
from plone.namedfile.interfaces import INamedField
from plone.namedfile.utils import set_headers, stream_data
from plone.registry.interfaces import IRegistry
from tempfile import NamedTemporaryFile
from tempfile import gettempdir
from z3c.form.browser.select import SelectWidget as z3cform_SelectWidget
from z3c.form.browser.text import TextWidget as z3cform_TextWidget
from z3c.form.browser.widget import HTMLInputWidget
from z3c.form.interfaces import IAddForm
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import NO_VALUE
from z3c.form.interfaces import IDataManager
from z3c.form.widget import FieldWidget
from z3c.form.widget import Widget
from zope.component import getUtility
from zope.component import ComponentLookupError
from zope.component import queryMultiAdapter
from zope.i18n import translate
from zope.interface import implementer
from zope.interface import implementsOnly
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces import NotFound
from zope.schema.interfaces import IChoice
from zope.schema.interfaces import ICollection
from zope.schema.interfaces import ISequence
from plone.app.widgets.utils import first_weekday

from plone.app.z3cform.converters import (
    DateWidgetConverter, DatetimeWidgetConverter, FileUploadConverter,
    MultiFileUploadConverter)
from plone.app.z3cform.interfaces import (
    IDatetimeWidget, IDateWidget, IAjaxSelectWidget,
    IRelatedItemsWidget, IQueryStringWidget, IRichTextWidget,
    ISelectWidget, IFileUploadWidget)

import json
import fnmatch
import os
import time
import mimetypes

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

    def __init__(self, *args, **kwargs):
        super(RichTextWidget, self).__init__(*args, **kwargs)
        self._pattern = None

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
            tool = getToolByName(self.context, "portal_membership")
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


class FileUploadWidget(BaseWidget, z3cform_TextWidget):
    implementsOnly(IFileUploadWidget)

    _base = DivWidget

    pattern = 'upload'
    pattern_options = BaseWidget.pattern_options.copy()
    maxFiles = 1000

    def _base_args(self):
        """Method which will calculate _base class arguments.

        Returns (as python dictionary):
            - `pattern`: pattern name
            - `pattern_options`: pattern options

        :returns: Arguments which will be passed to _base
        :rtype: dict
        """
        args = super(FileUploadWidget, self)._base_args()
        url = '%s/++widget++%s/@@upload/' % (
                    self.request.getURL(),
                    self.name)
        args.setdefault('pattern_options', {})
        args['pattern_options'] = {'url': url}
        args['pattern_options']['paramName'] = self.name
        if (INamedField.providedBy(self.field)):
            self.maxFiles = 1
        args['pattern_options']['maxFiles'] = self.maxFiles
        args['pattern_options']['isWidget'] = True
        args['pattern_options']['showTitle'] = False
        args['pattern_options']['autoCleanResults'] = False
        self.cleanup()
        loaded = []
        extractName = self.name + "uploaded"
        if getattr(self.request, extractName, None) is not None:
            files = self.request[extractName]
            if files:
                extracted = json.loads(str(files))
                for extracted_file in extracted:
                    if extracted_file['name'] != extracted_file['tmpname']:
                        tmpdir = gettempdir()
                        path = join(tmpdir, extracted_file['tmpname'])
                        file_ = open(path, 'r+b')
                        file_.seek(0, 2)  # end of file
                        tmpsize = file_.tell()
                        file_.seek(0)
                        file_.close()
                        dl_url = '%s/++widget++%s/@@download/' % (
                                  self.request.getURL(),
                                  self.name) + (extracted_file['tmpname'] +
                                                '?name=' +
                                                extracted_file['name'])
                        newfile = {'tmpname': extracted_file['tmpname'],
                                   'size': tmpsize,
                                   'url': dl_url,
                                   'name': extracted_file['name']}
                        loaded.append(newfile)

        if not IAddForm.providedBy(self.form):
            dm = queryMultiAdapter((self.context, self.field,), IDataManager)
        else:
            dm = None

        current_field_value = (
            dm.query()
            if ((dm is not None) and
                self.field.interface.providedBy(self.context))
            else None
        )
        if current_field_value and current_field_value != NO_VALUE:
            if not isinstance(current_field_value, list):
                current_field_value = [current_field_value]
            current_field_set = set(current_field_value)
            for item in current_field_set:
                dl_url = '%s/++widget++%s/@@downloadexisting/' % (
                             self.request.getURL(),
                             self.name) + item.filename
                info = {'name': item.filename,
                        'tmpname': item.filename,
                        'size': item.getSize(),
                        'url': dl_url,
                        }
                loaded.append(info)
        args['pattern_options']['existing'] = loaded
        return args

    def extract(self, default=NO_VALUE):
        """Extract all real FileUpload objects.
        """
        value = []
        extractName = self.name + "uploaded"
        if getattr(self.request, extractName, None) is not None:
            files = self.request[extractName]
            if files:
                extracted = json.loads(str(files))
                for extracted_file in extracted:
                    if extracted_file['name'] != extracted_file['tmpname']:
                        tmpdir = gettempdir()
                        path = join(tmpdir, extracted_file['tmpname'])
                        file_ = open(path, 'r+b')
                        newfile = {'name': extracted_file['name'],
                                   'file': file_, 'new': True,
                                   'temp': extracted_file['tmpname']}
                        value.append(newfile)
                    else:
                        oldfile = {'name': extracted_file['name'],
                                   'file': None, 'new': False}
                        value.append(oldfile)
        return value

    def render(self):
        """Render widget.

        :returns: Widget's HTML.
        :rtype: string
        """
        if self.mode != 'display':
            return super(FileUploadWidget, self).render()

        if not IAddForm.providedBy(self.form):
            dm = queryMultiAdapter((self.context, self.field,), IDataManager)
        else:
            dm = None
        ret_value = '<div class="files">'
        current_field_value = (
            dm.query()
            if ((dm is not None) and
                self.field.interface.providedBy(self.context))
            else None
        )
        if current_field_value and current_field_value != NO_VALUE:
            if not isinstance(current_field_value, list):
                current_field_value = [current_field_value]
            current_field_set = set(current_field_value)
            for item in current_field_set:
                ret_value = ret_value + '<div class="existfileupload">'
                dl_url = '%s/++widget++%s/@@downloadexisting/' % (
                             self.request.getURL(),
                             self.name) + item.filename
                ret_value = ret_value + '<a href=' + dl_url + '>'
                ret_value = ret_value + '<span class="filename">' + item.filename + '</span>'
                size = self.formatSize(item.getSize())
                ret_value = ret_value + '<span class="filesize"> ' + size + '</span>'
                ret_value = ret_value + '</div>'
        ret_value = ret_value + '</div>'
        return ret_value

    def formatSize(self, numBytes):
        """
        Format a human readable file size
        """
        if numBytes > 1000000000:
            return str(int(round(numBytes / (1024 * 1024 * 1024)))) + ' GB'
        if numBytes > 1000000:
            return str(int(round(numBytes / (1024 * 1024)))) + ' MB'
        return str(int(round(numBytes / 1024))) + ' KB'

    def cleanup(self):
        """
        look through upload directory and remove old uploads
        (older than 2 hrs)
        """
        now = time.time()
        tmpdir = gettempdir()
        for filename in os.listdir(tmpdir):
            if fnmatch.fnmatch(filename, '*FileUpload'):
                filepath = os.path.join(tmpdir, filename)
                if (os.stat(filepath).st_mtime) < now - 2 * 60 * 60:
                    os.unlink(filepath)


@implementer(IFieldWidget)
def FileUploadFieldWidget(field, request):
    return FieldWidget(field, FileUploadWidget(request))


class Upload(BrowserView):
    """Upload a file via ++widget++widget_name/@@upload"""

    implements(IPublishTraverse)

    def __call__(self):

        if hasattr(self.request, "REQUEST_METHOD"):
            # TODO: we should check errors in the creation process, and
            # broadcast those to the error template in JS
            if self.request["REQUEST_METHOD"] == "POST":
                if getattr(self.request, self.context.name, None) is not None:
                    files = self.request[self.context.name]
                    uploaded = self.upload(files)
                    if uploaded:
                        return json.dumps(uploaded)
                return json.dumps("")

    def upload(self, item):
        if item.filename:
            filename = safe_unicode(item.filename)
            item.seek(0, 2)  # end of file
            tmpsize = item.tell()
            tmpfile = NamedTemporaryFile(suffix='FileUpload', delete=False)
            item.seek(0)
            tmpfile.write(item.read())
            tmpfile.close()
            dlname = basename(tmpfile.name)
            dl_url = '%s/@@download/' % (
                     self.request.URL1) + dlname + '?name=' + filename
            info = {'name': filename,
                    'tmpname': dlname,
                    'size': tmpsize,
                    'url': dl_url,
                    }
        return info


class DownloadExisting(BrowserView):
    """Download a file via ++widget++widget_name/@@downloadexisting/filename"""

    implements(IPublishTraverse)

    def __init__(self, context, request):
        super(BrowserView, self).__init__(context, request)
        self.filename = None

    def publishTraverse(self, request, name):

        if self.filename is None:  # ../@@download/filename
            self.filename = name
        else:
            raise NotFound(self, name, request)

        return self

    def __call__(self):

        if self.context.form is not None:
            content = aq_inner(self.context.form.getContent())
        else:
            content = aq_inner(self.context.context)
        field = aq_inner(self.context.field)

        dm = queryMultiAdapter((content, field,), IDataManager)
        file_list = dm.query()
        if file_list == NO_VALUE:
            return None
        file_ = None
        if not isinstance(file_list, list):
            file_list = [file_list]
        for curr_file in file_list:
            if curr_file.filename == self.filename:
                file_ = curr_file
        filename = getattr(file_, 'filename', '')
        if not file_:
            return None
        set_headers(file_, self.request.response, filename=filename)
        return stream_data(file_)


class Download(BrowserView):
    """Download a file via ++widget++widget_name/@@download/filename"""

    implements(IPublishTraverse)

    def __init__(self, context, request):
        super(BrowserView, self).__init__(context, request)
        self.filename = None

    def publishTraverse(self, request, name):

        if self.filename is None:  # ../@@download/filename
            self.filename = name
        else:
            raise NotFound(self, name, request)

        return self

    def __call__(self):

        if getattr(self.request, "name", None) is not None:
            filename = self.request['name']
        tmpdir = gettempdir()
        filepath = os.path.join(tmpdir, self.filename)
        try:
            file_ = open(filepath)
        except IOError:
            return

        file_.seek(0, 2)  # end of file
        tmpsize = file_.tell()
        file_.seek(0)
        contenttype = 'application/octet-stream'
        filename = safe_unicode(filename)
        if filename:
            extension = os.path.splitext(filename)[1].lower()
            contenttype = mimetypes.types_map.get(extension,
                                                  'application/octet-stream')
        self.request.response.setHeader("Content-Type", contenttype)
        self.request.response.setHeader("Content-Length", tmpsize)
        if filename is not None:
            self.request.response.setHeader("Content-Disposition",
                                            "attachment; filename=\"%s\""
                                             % filename)
        return filestream_iterator(filepath, 'rb')



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
