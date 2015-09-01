# -*- coding: utf-8 -*-

try:
    import unittest2 as unittest
except ImportError:  # pragma: nocover
    import unittest  # pragma: nocover
    assert unittest  # pragma: nocover
from zope.publisher.browser import TestRequest as BaseTestRequest
from plone.app.widgets.interfaces import IWidgetsLayer
from zope.interface import implements, Interface
from plone.app.z3cform.widget import Upload, Download, DownloadExisting
from plone.namedfile.field import NamedFile
from plone.namedfile.file import NamedFile as CMPNamedFile

from zope.interface import alsoProvides
from z3c.form.interfaces import IFormLayer, IAddForm, IDataManager, IField
from z3c.form import datamanager
from zope.schema import List
from mock import Mock
from tempfile import NamedTemporaryFile
from os.path import basename
from stat import ST_ATIME, ST_MTIME
from zope.interface import directlyProvides
from zope.component import getMultiAdapter
from zope.component import provideAdapter
from ZPublisher.HTTPRequest import FileUpload
from cgi import FieldStorage
from tempfile import TemporaryFile
from zope.publisher.interfaces import NotFound
import json
import os


class TestRequest(BaseTestRequest):
    implements(IWidgetsLayer)


class DummyContext(object):

    implements(Interface)
    name = 'dummy'

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def getContent(self):
        return self.context


class FileUploadWidgetTests(unittest.TestCase):

    def setUp(self):
        from plone.app.z3cform.widget import FileUploadWidget

        self.request = TestRequest(environ=
        {'HTTP_ACCEPT_LANGUAGE': 'en', 'REQUEST_METHOD': 'POST', 'files[]': None})
        alsoProvides(self.request, IFormLayer)
        self.widget = FileUploadWidget(self.request)
        self.field = List(__name__='files',
                     value_type=NamedFile())
        alsoProvides(self.field, IField)
        self.context = DummyContext()
        self.widget.context = self.context
        self.field.interface = Interface
        provideAdapter(datamanager.AttributeField)
        self.widget.field = self.field
        self.form = Mock()
        directlyProvides(self.form, IAddForm)

    def test_widget(self):
        self.widget.form = self.form
        self.widget.name = 'dummy'
        self.assertEqual(
            {'pattern': 'upload',
            'pattern_options': {'url': 'http://127.0.0.1/++widget++dummy/@@upload/',
            'maxFiles': 1000, 'existing': [], 'paramName': 'dummy',
            'isWidget': True, 'autoCleanResults': False, 'showTitle': False}},
            self.widget._base_args(),
        )
        self.widget.form = None
        dm = getMultiAdapter((self.widget.context, self.widget.field), IDataManager)
        dm.set(CMPNamedFile(data='Just some text', filename=u'file.txt'))
        self.assertEqual(
            {'pattern': 'upload',
            'pattern_options': {'url': 'http://127.0.0.1/++widget++dummy/@@upload/',
                                'maxFiles': 1000, 'existing': [{'name': u'file.txt',
                                'size': 14,
                                'tmpname': u'file.txt',
                                'url': u'http://127.0.0.1/++widget++dummy/@@downloadexisting/file.txt'}],
                                'paramName': 'dummy',
                                'isWidget': True, 'autoCleanResults': False, 'showTitle': False}},
            self.widget._base_args(),
        )

    def test_render(self):
        self.widget.form = self.form
        self.widget.name = 'dummy'
        self.assertEqual('<div class="pat-upload"' +
                         ' data-pat-upload=' +
                         '"{&quot;maxFiles&quot;: 1000, &quot;url&quot;: &quot;http://127.0.0.1/++widget++dummy/@@upload/&quot;,' +
                         ' &quot;existing&quot;: [], &quot;isWidget&quot;: true, &quot;autoCleanResults&quot;: false,' +
                         ' &quot;paramName&quot;: &quot;dummy&quot;, &quot;showTitle&quot;: false}"/>'
            ,
            self.widget.render(),
        )
        self.widget.mode = 'display'
        self.assertEqual('<div class="files"></div>',
            self.widget.render(),
        )
        self.widget.mode = 'display'
        self.widget.form = None
        dm = getMultiAdapter((self.widget.context, self.widget.field), IDataManager)
        dm.set(CMPNamedFile(data='Just some text', filename=u'file.txt'))
        self.assertEqual(u'<div class="files"><div class="existfileupload">' +
                         '<a href=http://127.0.0.1/++widget++dummy/@@downloadexisting/file.txt>' +
                         '<span class="filename">file.txt</span>' +
                         '<span class="filesize"> 0 KB</span></div></div>',
            self.widget.render(),
        )

    def test_format_size(self):
        self.assertEqual('1 KB',
            self.widget.formatSize(1234),
        )
        self.assertEqual('11 MB',
            self.widget.formatSize(12345678),
        )
        self.assertEqual('11 GB',
            self.widget.formatSize(12345678901),
        )

    def test_one_file(self):
        self.widget.form = self.form
        self.widget.name = 'dummy'
        self.widget.maxFiles = 1
        self.assertEqual(
            {'pattern': 'upload',
            'pattern_options': {'url': 'http://127.0.0.1/++widget++dummy/@@upload/',
            'maxFiles': 1, 'existing': [],
            'isWidget': True, 'autoCleanResults': False,
            'paramName': 'dummy', 'showTitle': False}},
            self.widget._base_args(),
        )

    def test_form_error(self):
        self.widget.form = self.form
        self.widget.name = 'dummy'
        loaded = []
        tmpfile = NamedTemporaryFile(suffix='FileUpload', delete=False)
        tmpfile.write('Some More Data')
        tmpname = basename(tmpfile.name)
        name = u'errordata.txt'
        tmpfile.close()
        info = {'name': name,
                'tmpname': tmpname,
                }
        loaded.append(info)
        self.widget.name = 'dummy'
        uploaded = self.widget.name + 'uploaded'
        self.request.form[uploaded] = json.dumps(loaded)
        setattr(self.request, uploaded, 'x')
        baseArgs = self.widget._base_args()
        self.assertEqual(baseArgs['pattern_options']['existing'][0]['name'],
                         'errordata.txt', )

    def test_converter_existing_data(self):
        from plone.app.z3cform.converters import FileUploadConverter
        dm = getMultiAdapter((self.widget.context, self.widget.field), IDataManager)
        dm.set(CMPNamedFile(data='Just a bunch of text', filename=u'oldfile.txt'))

        converter = FileUploadConverter(self.field, self.widget)

        oldfile = {'name': u'oldfile.txt', 'file': None, 'new': False}
        named_files = converter.toFieldValue(oldfile)
        self.assertTrue(named_files)
        for named_file in named_files:
            self.assertEqual(u'oldfile.txt',
                             named_file.filename,)
            self.assertTrue(isinstance(named_file, CMPNamedFile))

    def test_data_converter(self):
        from plone.app.z3cform.converters import FileUploadConverter
        converter = FileUploadConverter(self.field, self.widget)

        self.assertEqual(
            converter.field.missing_value,
            converter.toFieldValue(None),
        )

        self.assertEqual('somevalue', converter.toWidgetValue('somevalue'))

        self.widget.form = self.form
        tmpfile = NamedTemporaryFile(suffix='FileUpload', delete=False)
        tmpfile.write('Some Data')
        tmpname = basename(tmpfile.name)
        name = u'somedata.txt'
        newfile = {'name': name, 'file': tmpfile, 'new': True, 'temp': tmpname}
        named_files = converter.toFieldValue(newfile)
        self.assertTrue(named_files)
        for named_file in named_files:
            self.assertEqual(u'somedata.txt',
                             named_file.filename,)
            self.assertTrue(isinstance(named_file, CMPNamedFile))
        self.widget.form = None

    def test_widget_extract(self):
        loaded = []
        tmpfile = NamedTemporaryFile(suffix='FileUpload', delete=False)
        tmpfile.write('Some More Data')
        tmpname = basename(tmpfile.name)
        name = u'somemoredata.txt'
        tmpfile.close()
        info = {'name': name,
                'tmpname': tmpname,
                }
        loaded.append(info)
        self.widget.name = 'dummy'
        uploaded = self.widget.name + 'uploaded'
        self.request.form[uploaded] = json.dumps(loaded)
        setattr(self.request, uploaded, 'x')
        extracted = self.widget.extract()
        for extract in extracted:
            self.assertEqual(u'somemoredata.txt',
                             extract['name'],)
            self.assertTrue(extract['new'])
            self.assertTrue(isinstance(extract['file'], file))
        loaded = []
        dm = getMultiAdapter((self.widget.context, self.widget.field), IDataManager)
        dm.set(CMPNamedFile(data='Just a bunch of text', filename=u'extfile.txt'))
        more_info = {'name': u'extfile.txt',
                'tmpname': u'extfile.txt',
                }
        loaded.append(more_info)
        self.request.form[uploaded] = json.dumps(loaded)
        setattr(self.request, uploaded, 'x')
        extracted = self.widget.extract()
        for extract in extracted:
            self.assertEqual(u'extfile.txt',
                             extract['name'],)
            self.assertFalse(extract['new'])
            self.assertFalse(extract['file'])
        os.unlink(tmpfile.name)

    def test_widget_cleanup(self):
        tmpfile = NamedTemporaryFile(suffix='FileUpload', delete=False)
        tmpfile.write('Even More Data')
        tmpfile.flush()
        tmpfile.close()
        st = os.stat(tmpfile.name)
        atime = st[ST_ATIME]  # access time
        mtime = st[ST_MTIME]  # modification time
        new_mtime = mtime - 3 * 60 * 60  #new modification time 3 hours ago
        #modify the file timestamp
        os.utime(tmpfile.name, (atime, new_mtime))
        self.widget.cleanup()
        self.assertFalse(os.path.exists(tmpfile.name))

    def test_fieldwidget(self):
        from plone.app.z3cform.widget import FileUploadWidget
        from plone.app.z3cform.widget import FileUploadFieldWidget
        field = Mock(__name__='field', title=u'', required=True)
        request = Mock()
        widget = FileUploadFieldWidget(field, request)
        self.assertTrue(isinstance(widget, FileUploadWidget))
        self.assertIs(widget.field, field)
        self.assertIs(widget.request, request)

    def test_upload(self):
        upload = Upload(self.context, self.request)
        setattr(self.request, "REQUEST_METHOD", "POST")
        json_value = upload()
        self.assertEqual(json_value, '""',)

    def test_upload_file(self):
        fp = TemporaryFile('w+b')
        fp.write('foobar')
        fp.seek(0)
        filename = 'test.xml'
        env = {'REQUEST_METHOD': 'PUT'}
        headers = {'content-type': 'text/plain',
                   'content-length': str(len('foobar')),
                   'content-disposition': 'attachment; filename=%s' % filename}
        files_ = FileUpload(FieldStorage(fp=fp, environ=env, headers=headers))
        fileids = self.context.name + 'fileids'
        request = TestRequest(environ={'HTTP_ACCEPT_LANGUAGE': 'en', 'REQUEST_METHOD': 'POST', 'dummy': files_, fileids: 'fXXXXX'})
        setattr(request, "dummy", "stuff")
        setattr(request, "URL1", "http://127.0.0.1")
        upload = Upload(self.context, request)
        setattr(request, "REQUEST_METHOD", "POST")
        json_value = upload()
        self.assertTrue('"size": 6' in json_value)
        self.assertTrue('"name": "test.xml"' in json_value)
        request = TestRequest(environ={'HTTP_ACCEPT_LANGUAGE': 'en', 'REQUEST_METHOD': 'POST', 'dummy': None})

    def test_download(self):
        request = TestRequest(environ={'HTTP_ACCEPT_LANGUAGE': 'en', 'REQUEST_METHOD': 'POST', 'name': u'somedata.txt'})
        setattr(request, "name", u'somedata.txt')
        download = Download(self.context, request)
        pt = download.publishTraverse(request, 'TestFilename')
        self.assertEqual(pt.filename, 'TestFilename',)
        download.filename = 'NotFoundTest'
        with self.assertRaises(NotFound) as cm:
            download.publishTraverse(request, 'TestFilename')
        the_exception = cm.exception
        self.assertEqual(the_exception.name, 'TestFilename',)
        tmpfile = NamedTemporaryFile(suffix='FileUpload', delete=False)
        tmpfile.write('Some Data')
        tmpname = basename(tmpfile.name)
        download.filename = tmpname
        dl = download()
        self.assertEqual(dl.name, tmpfile.name,)
        os.unlink(tmpfile.name)
        download.filename = 'NotFoundTest'
        self.assertRaises(IOError, download())

    def test_download_existing(self):
        download = DownloadExisting(self.context, self.request)
        pt = download.publishTraverse(self.request, 'TestFilename')
        self.assertEqual(pt.filename, 'TestFilename',)
        download.filename = 'NotFoundTest'
        with self.assertRaises(NotFound) as cm:
            download.publishTraverse(self.request, 'TestFilename')
        the_exception = cm.exception
        self.assertEqual(the_exception.name, 'TestFilename',)
        self.context.form = None
        self.context.context = self.widget.context
        self.context.field = self.widget.field
        self.assertFalse(download())
        dm = getMultiAdapter((self.widget.context, self.widget.field), IDataManager)
        dm.set(CMPNamedFile(data='Just a bunch of text', filename=u'extfile.txt'))
        self.assertFalse(download())
        download.filename = u'extfile.txt'
        dl = download()
        self.assertEqual(dl, 'Just a bunch of text',)
        self.assertEqual(self.request.response.getHeader('Content-Disposition'),
                         "attachment; filename*=UTF-8''extfile.txt",)
        self.context.form = DummyContext()
        self.context.form.context = self.widget.context
        dm = getMultiAdapter((self.widget.context, self.widget.field), IDataManager)
        dm.set(CMPNamedFile(data='Just a bunch of silly text', filename=u'sillyfile.txt'))
        download.filename = u'sillyfile.txt'
        dl = download()
        self.assertEqual(dl, 'Just a bunch of silly text',)
        self.assertEqual(self.request.response.getHeader('Content-Disposition'),
                         "attachment; filename*=UTF-8''sillyfile.txt",)
