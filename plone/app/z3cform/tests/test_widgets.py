# -*- coding: utf-8 -*-
from datetime import date
from datetime import datetime
from datetime import time
from json import loads
from lxml import html
from mock import Mock
from plone.app.contentlisting.contentlisting import ContentListing
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.widgets.utils import NotImplemented as PatternNotImplemented
from plone.app.z3cform.tests.layer import PAZ3CForm_INTEGRATION_TESTING
from plone.app.z3cform.widget import BaseWidget
from plone.app.z3cform.widget import DateWidget
from plone.app.z3cform.widget import RelatedItemsWidget
from plone.autoform.directives import widget
from plone.autoform.form import AutoExtensibleForm
from plone.dexterity.fti import DexterityFTI
from plone.registry.interfaces import IRegistry
from plone.supermodel.model import Schema
from plone.testing.zca import UNIT_TESTING
from plone.uuid.interfaces import IUUID
from Products.CMFPlone.interfaces import IMarkupSchema
from z3c.form.form import EditForm
from z3c.form.form import Form
from z3c.form.interfaces import IFormLayer
from z3c.form.widget import FieldWidget
from z3c.relationfield.relation import RelationValue
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component import provideUtility
from zope.component.globalregistry import base
from zope.globalrequest import setRequest
from zope.interface import alsoProvides
from zope.interface import Interface
from zope.interface import provider
from zope.intid.interfaces import IIntIds
from zope.pagetemplate.interfaces import IPageTemplate
from zope.publisher.browser import TestRequest
from zope.schema import BytesLine
from zope.schema import Choice
from zope.schema import Date
from zope.schema import Datetime
from zope.schema import List
from zope.schema import Set
from zope.schema import TextLine
from zope.schema import Time
from zope.schema import Tuple
from zope.schema import vocabulary
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

import json
import mock
import pytz
import six
import unittest


@provider(IVocabularyFactory)
def example_vocabulary_factory(context, query=None):
    items = [u'One', u'Two', u'Three']
    tmp = SimpleVocabulary(
        [
            SimpleTerm(
                item.lower(),  # value
                token='token_{0}'.format(item.lower()),
                title=item,
            )
            for item in items
            if query is None or query.lower() in item.lower()
        ],
    )
    tmp.test = 1
    return tmp


class BaseWidgetTests(unittest.TestCase):

    def setUp(self):
        self.request = TestRequest(environ={'HTTP_ACCEPT_LANGUAGE': 'en'})
        self.field = TextLine(__name__='textlinefield')
        self.maxDiff = 999999

    def test_widget_pattern_notimplemented(self):
        widget = BaseWidget(self.request)
        widget.field = self.field

        self.assertRaises(
            PatternNotImplemented,
            widget._base_args,
        )

        widget.pattern = 'example'

        self.assertEqual(
            {
                'pattern': 'example',
                'pattern_options': {},
            },
            widget._base_args(),
        )

    def test_widget_base_notimplemented(self):
        from plone.app.widgets.base import InputWidget
        from plone.app.z3cform.widget import BaseWidget

        widget = BaseWidget(self.request)
        widget.field = self.field
        widget.pattern = 'example'

        self.assertRaises(
            PatternNotImplemented,
            widget.render,
        )

        widget._base = InputWidget

        self.assertEqual(
            '<input class="pat-example" type="text"/>',
            widget.render(),
        )

    def test_widget_base_custom_css(self):
        from plone.app.widgets.base import InputWidget
        from plone.app.z3cform.widget import BaseWidget

        widget = BaseWidget(self.request)
        widget.field = self.field
        widget.pattern = 'example'
        widget.klass = 'very-custom-class'
        widget._base = InputWidget

        self.assertEqual(
            '<input class="pat-example very-custom-class" type="text"/>',
            widget.render())

    def test_widget_base_pattern_options_with_functions(self):
        from plone.app.widgets.base import InputWidget
        from plone.app.z3cform.widget import BaseWidget

        widget = BaseWidget(self.request)
        widget.context = 'testcontext'
        widget.field = self.field
        widget.pattern = 'example'
        widget._base = InputWidget
        widget.pattern_options = {
            'subdict': {
                'subsubnormal': 789,
                'subsublist': [7, 8, 9, lambda x: x],
                'subsubtuple': (7, 8, 9, lambda x: x),
            },
        }
        output = widget.render()
        # output is something like
        #
        # <input class="pat-example"
        #        type="text"
        #        data-pat-example="$JSON_ENCODED_OPTIONS" />'
        self.assertRegexpMatches(widget.render(), '<input .*/>')
        # We cannot foresee how the options are encoded
        # so we will extract the attributes with lxml
        # and be sure that they will match what we expect
        observed_attrib = html.fromstring(output).attrib
        self.assertEqual(
            sorted(observed_attrib),
            ['class', 'data-pat-example', 'type'],
        )
        self.assertEqual(observed_attrib['class'], 'pat-example')
        self.assertEqual(observed_attrib['type'], 'text')
        self.assertDictEqual(
            loads(observed_attrib['data-pat-example']),
            {
                'subdict': {
                    'subsubnormal': 789,
                    'subsublist': [7, 8, 9, 'testcontext'],
                    'subsubtuple': [7, 8, 9, 'testcontext'],
                },
            },
        )


class DateWidgetTests(unittest.TestCase):

    def setUp(self):
        from plone.app.z3cform.widget import DateWidget

        self.request = TestRequest(environ={'HTTP_ACCEPT_LANGUAGE': 'en'})
        self.field = Date(__name__='datefield')
        self.field.required = False
        self.widget = DateWidget(self.request)
        self.widget.field = self.field
        self.widget.pattern_options = {'date': {'firstDay': 0}}

    def test_widget(self):
        current_year = datetime.today().year
        self.assertEqual(
            {
                'name': None,
                'pattern': 'date-picker',
                'pattern_options': {'behavior': 'native',
                                    'clear': 'Clear',
                                    'date': {'firstDay': 0},
                                    'first-day': 0,
                                    'today': 'Today',
                                    'week-numbers': 'show'},
                'value': '',
            },
            self.widget._base_args(),
        )

    def test_widget_required(self):
        """Required fields should not have a "Clear" button.
        """
        self.field.required = True
        base_args = self.widget._base_args()
        self.assertEqual(base_args['pattern_options']['clear'], False)

    def test_data_converter(self):
        from plone.app.z3cform.widget import DateWidgetConverter
        converter = DateWidgetConverter(self.field, self.widget)

        self.assertEqual(
            converter.field.missing_value,
            converter.toFieldValue(''),
        )

        self.assertEqual(
            date(2000, 10, 30),
            converter.toFieldValue('2000-10-30'),
        )

        self.assertEqual(
            date(21, 10, 30),
            converter.toFieldValue('21-10-30'),
        )

        self.assertEqual(
            '',
            converter.toWidgetValue(converter.field.missing_value),
        )

        self.assertEqual(
            '2000-10-30',
            converter.toWidgetValue(date(2000, 10, 30)),
        )

        self.assertEqual(
            '21-10-30',
            converter.toWidgetValue(date(21, 10, 30)),
        )

    def test_fieldwidget(self):
        from plone.app.z3cform.widget import DateFieldWidget
        from plone.app.z3cform.widget import DateWidget
        field = Mock(__name__='field', title=u'', required=True)
        request = Mock()
        widget = DateFieldWidget(field, request)
        self.assertTrue(isinstance(widget, DateWidget))
        self.assertIs(widget.field, field)
        self.assertIs(widget.request, request)


class DatetimeWidgetTests(unittest.TestCase):

    def setUp(self):
        from plone.app.z3cform.widget import DatetimeWidget

        self.request = TestRequest(environ={'HTTP_ACCEPT_LANGUAGE': 'en'})
        self.field = Datetime(__name__='datetimefield')
        self.field.required = False
        self.widget = DatetimeWidget(self.request)
        self.widget.field = self.field
        self.widget.pattern_options = {
            'date': {'firstDay': 0},
            'time': {'interval': 15},
        }

    def test_widget(self):
        current_year = datetime.today().year
        self.assertEqual(
            {
                'name': None,
                'pattern': 'datetime-picker',
                'pattern_options': {'behavior': 'native',
                                    'clear': 'Clear',
                                    'date': {'firstDay': 0},
                                    'first-day': 0,
                                    'time': {'interval': 15},
                                    'today': 'Today',
                                    'week-numbers': 'show'},
                'value': '',
            },
            self.widget._base_args(),
        )

    def test_widget_required(self):
        """Required fields should not have a "Clear" button.
        """
        self.field.required = True
        base_args = self.widget._base_args()
        self.assertEqual(base_args['pattern_options']['clear'], False)

    def test_data_converter(self):
        from plone.app.z3cform.widget import DatetimeWidgetConverter
        converter = DatetimeWidgetConverter(self.field, self.widget)

        self.assertEqual(
            converter.toFieldValue(''),
            converter.field.missing_value,
        )

        self.assertEqual(
            converter.toFieldValue('2000-10-30T15:40'),
            datetime(2000, 10, 30, 15, 40),
        )

        self.assertEqual(
            converter.toFieldValue('21-10-30T15:40'),
            datetime(21, 10, 30, 15, 40),
        )

        self.assertEqual(
            converter.toWidgetValue(converter.field.missing_value),
            '',
        )

        self.assertEqual(
            converter.toWidgetValue(datetime(2000, 10, 30, 15, 40)),
            '2000-10-30T15:40',
        )

        self.assertEqual(
            converter.toWidgetValue(datetime(21, 10, 30, 15, 40)),
            '21-10-30T15:40',
        )

    def test_data_converter__no_timezone(self):
        """When no timezone is set, don't apply one.
        """
        from plone.app.z3cform.widget import DatetimeWidgetConverter
        context = Mock()

        dt = datetime(2013, 11, 13, 10, 20)
        setattr(context, self.field.getName(), dt)
        self.widget.context = context
        self.widget.default_timezone = None

        converter = DatetimeWidgetConverter(self.field, self.widget)
        self.assertEqual(
            converter.toFieldValue('2013-11-13T10:20'),
            datetime(2013, 11, 13, 10, 20),
        )

        # cleanup
        self.widget.context = None
        self.widget.default_timezone = None

    def test_data_converter__timezone_id(self):
        """When a (pytz) timezone id is set, use that.
        """
        from plone.app.z3cform.widget import DatetimeWidgetConverter
        context = Mock()

        dt = datetime(2013, 11, 13, 10, 20)
        setattr(context, self.field.getName(), dt)
        self.widget.context = context
        self.widget.default_timezone = 'Europe/Amsterdam'
        tz = pytz.timezone('Europe/Amsterdam')

        converter = DatetimeWidgetConverter(self.field, self.widget)
        self.assertEqual(
            converter.toFieldValue('2013-11-13T10:20'),
            tz.localize(datetime(2013, 11, 13, 10, 20)),
        )

        # cleanup
        self.widget.context = None
        self.widget.default_timezone = None

    def test_data_converter__timezone_callback(self):
        """When a timezone callback is set, returning a (pytz) timezone id,
        use that.
        """
        from plone.app.z3cform.widget import DatetimeWidgetConverter
        context = Mock()

        dt = datetime(2013, 11, 13, 10, 20)
        setattr(context, self.field.getName(), dt)
        self.widget.context = context
        self.widget.default_timezone = lambda context: 'Europe/Amsterdam'
        tz = pytz.timezone('Europe/Amsterdam')

        converter = DatetimeWidgetConverter(self.field, self.widget)
        self.assertEqual(
            converter.toFieldValue('2013-11-13T10:20'),
            tz.localize(datetime(2013, 11, 13, 10, 20)),
        )

        # cleanup
        self.widget.context = None
        self.widget.default_timezone = None

    def test_fieldwidget(self):
        from plone.app.z3cform.widget import DatetimeFieldWidget
        from plone.app.z3cform.widget import DatetimeWidget
        field = Mock(__name__='field', title=u'', required=True)
        request = Mock()
        widget = DatetimeFieldWidget(field, request)
        self.assertTrue(isinstance(widget, DatetimeWidget))
        self.assertIs(widget.field, field)
        self.assertIs(widget.request, request)


class TimeWidgetTests(unittest.TestCase):

    def setUp(self):
        from plone.app.z3cform.widget import TimeWidget

        self.request = TestRequest(environ={'HTTP_ACCEPT_LANGUAGE': 'en'})
        self.field = Time(__name__='timefield')
        self.field.required = False
        self.widget = TimeWidget(self.request)
        self.widget.field = self.field

    def test_widget(self):
        self.assertIn("<input type=\"time\"", self.widget.render())

    def test_data_converter(self):
        from plone.app.z3cform.converters import TimeWidgetConverter
        converter = TimeWidgetConverter(self.field, self.widget)

        self.assertEqual(
            converter.toFieldValue(''),
            converter.field.missing_value,
        )

        self.assertEqual(
            converter.toFieldValue('15:40'),
            time(15, 40),
        )

        self.assertEqual(
            converter.toWidgetValue(converter.field.missing_value),
            '',
        )

        self.assertEqual(
            converter.toWidgetValue(time(15, 40)),
            '15:40',
        )

    def test_fieldwidget(self):
        from plone.app.z3cform.widget import TimeFieldWidget
        from plone.app.z3cform.widget import TimeWidget
        field = Mock(__name__='field', title=u'', required=True)
        request = Mock()
        widget = TimeFieldWidget(field, request)
        self.assertTrue(isinstance(widget, TimeWidget))
        self.assertIs(widget.field, field)
        self.assertIs(widget.request, request)


class SelectWidgetTests(unittest.TestCase):

    def setUp(self):
        self.request = TestRequest(environ={'HTTP_ACCEPT_LANGUAGE': 'en'})
        alsoProvides(self.request, IFormLayer)

        # ITerms Adapters are needed for data converter
        from z3c.form import term

        import zope.component
        zope.component.provideAdapter(term.CollectionTerms)
        zope.component.provideAdapter(term.CollectionTermsVocabulary)
        zope.component.provideAdapter(term.CollectionTermsSource)

    def tearDown(self):
        from z3c.form import term
        base.unregisterAdapter(term.CollectionTerms)
        base.unregisterAdapter(term.CollectionTermsVocabulary)
        base.unregisterAdapter(term.CollectionTermsSource)

    def test_widget(self):
        from plone.app.z3cform.widget import SelectWidget
        widget = SelectWidget(self.request)
        widget.id = 'test-widget'
        widget.field = Choice(
            __name__='selectfield',
            values=['one', 'two', 'three'],
        )
        widget.terms = widget.field.vocabulary
        widget.field.required = True
        self.assertEqual(
            {
                'multiple': None,
                'name': None,
                'pattern_options': {},
                'pattern': 'select2',
                'value': (),
                'items': [
                    ('one', 'one'),
                    ('two', 'two'),
                    ('three', 'three'),
                ],
            },
            widget._base_args(),
        )

        widget.field.required = False
        self.assertEqual(
            {
                'multiple': None,
                'name': None,
                'pattern_options': {'allowClear': True},
                'pattern': 'select2',
                'value': (),
                'items': [
                    (u'', u''),
                    ('one', 'one'),
                    ('two', 'two'),
                    ('three', 'three'),
                ],
            },
            widget._base_args(),
        )

        widget.field.required = True
        widget.multiple = True
        self.assertEqual(
            {
                'multiple': True,
                'name': None,
                'pattern_options': {'separator': ';'},
                'pattern': 'select2',
                'value': (),
                'items': [
                    ('one', 'one'),
                    ('two', 'two'),
                    ('three', 'three'),
                ],
            },
            widget._base_args(),
        )

        widget.field.required = False
        widget.multiple = True
        self.assertEqual(
            {
                'multiple': True,
                'name': None,
                'pattern_options': {'allowClear': True, 'separator': ';'},
                'pattern': 'select2',
                'value': (),
                'items': [
                    ('one', 'one'),
                    ('two', 'two'),
                    ('three', 'three'),
                ],
            },
            widget._base_args(),
        )

        widget.value = 'one'
        self.assertEqual(
            {
                'multiple': True,
                'name': None,
                'pattern_options': {'allowClear': True, 'separator': ';'},
                'pattern': 'select2',
                'value': ('one'),
                'items': [
                    ('one', 'one'),
                    ('two', 'two'),
                    ('three', 'three'),
                ],
            },
            widget._base_args(),
        )

    def test_widget_list_orderable(self):
        from plone.app.z3cform.widget import SelectWidget
        widget = SelectWidget(self.request)
        widget.id = 'test-widget'
        widget.separator = '.'
        widget.field = List(
            __name__='selectfield',
            value_type=Choice(values=['one', 'two', 'three']),
        )
        widget.terms = widget.field.value_type.vocabulary
        self.assertEqual(
            {
                'multiple': True,
                'name': None,
                'pattern_options': {
                    'orderable': True, 'separator': '.'},
                'pattern': 'select2',
                'value': (),
                'items': [
                    ('one', 'one'),
                    ('two', 'two'),
                    ('three', 'three'),
                ],
            },
            widget._base_args(),
        )

    def test_widget_tuple_orderable(self):
        from plone.app.z3cform.widget import SelectWidget
        widget = SelectWidget(self.request)
        widget.id = 'test-widget'
        widget.field = Tuple(
            __name__='selectfield',
            value_type=Choice(values=['one', 'two', 'three']),
        )
        widget.terms = widget.field.value_type.vocabulary
        self.assertEqual(
            {
                'multiple': True,
                'name': None,
                'pattern_options': {
                    'orderable': True, 'separator': ';'},
                'pattern': 'select2',
                'value': (),
                'items': [
                    ('one', 'one'),
                    ('two', 'two'),
                    ('three', 'three'),
                ],
            },
            widget._base_args(),
        )

    def test_widget_set_not_orderable(self):
        from plone.app.z3cform.widget import SelectWidget
        widget = SelectWidget(self.request)
        widget.id = 'test-widget'
        # A set is not orderable
        widget.field = Set(
            __name__='selectfield',
            value_type=Choice(values=['one', 'two', 'three']),
        )
        widget.terms = widget.field.value_type.vocabulary
        self.assertEqual(
            {
                'multiple': True,
                'name': None,
                'pattern_options': {'separator': ';'},
                'pattern': 'select2',
                'value': (),
                'items': [
                    ('one', 'one'),
                    ('two', 'two'),
                    ('three', 'three'),
                ],
            },
            widget._base_args(),
        )

    def test_widget_extract(self):
        from plone.app.z3cform.widget import SelectWidget
        widget = SelectWidget(self.request)
        widget.field = Choice(
            __name__='selectfield',
            values=['one', 'two', 'three'],
        )
        widget.name = 'selectfield'
        self.request.form['selectfield'] = 'one'
        self.assertEqual(widget.extract(), 'one')
        widget.multiple = True
        self.request.form['selectfield'] = 'one;two'
        self.assertEqual(widget.extract(), 'one;two')

    def test_data_converter_list(self):
        from plone.app.z3cform.converters import SelectWidgetConverter
        from plone.app.z3cform.widget import SelectWidget

        field = List(
            __name__='listfield',
            value_type=Choice(
                __name__='selectfield',
                values=['one', 'two', 'three'],
            ),
        )
        widget = SelectWidget(self.request)
        widget.field = field
        widget.multiple = True
        converter = SelectWidgetConverter(field, widget)

        self.assertEqual(
            converter.toFieldValue(''),
            field.missing_value,
        )

        self.assertEqual(
            converter.toFieldValue('one;two;three'),
            ['one', 'two', 'three'],
        )

        self.assertEqual(
            converter.toWidgetValue([]),
            [],
        )

        widget.separator = ','
        self.assertEqual(
            converter.toFieldValue('one,two,three'),
            ['one', 'two', 'three'],
        )
        self.assertRaises(
            LookupError,
            converter.toFieldValue, 'one;two;three',
        )

        self.assertEqual(
            converter.toWidgetValue(['one', 'two', 'three']),
            ['one', 'two', 'three'],
        )

    def test_data_converter_tuple(self):
        from plone.app.z3cform.converters import SelectWidgetConverter
        from plone.app.z3cform.widget import SelectWidget

        field = Tuple(
            __name__='tuplefield',
            value_type=Choice(
                __name__='selectfield',
                values=['one', 'two', 'three'],
            ),
        )
        widget = SelectWidget(self.request)
        widget.field = field
        widget.multiple = True
        converter = SelectWidgetConverter(field, widget)

        self.assertEqual(
            converter.toFieldValue(''),
            field.missing_value,
        )

        self.assertEqual(
            converter.toFieldValue('one;two;three'),
            ('one', 'two', 'three'),
        )

        self.assertEqual(
            converter.toWidgetValue(tuple()),
            [],
        )

        self.assertEqual(
            converter.toWidgetValue(('one', 'two', 'three')),
            ['one', 'two', 'three'],
        )

    def test_data_converter_handles_empty_value(self):
        from plone.app.z3cform.converters import SelectWidgetConverter
        from plone.app.z3cform.widget import SelectWidget

        field = Tuple(__name__='tuplefield',
                      value_type=Choice(__name__='selectfield',
                                        values=['one', 'two', 'three']))
        widget = SelectWidget(self.request)
        widget.field = field
        widget.multiple = True
        converter = SelectWidgetConverter(field, widget)

        self.assertEqual(
            converter.toFieldValue((u'',)),
            field.missing_value,
        )

    def test_widget_optgroup(self):
        """
        If the widget vocabulary is a mapping <optgroup>'s are rendered.
        """
        from plone.app.z3cform.widget import SelectWidget
        from z3c.form import term
        widget = SelectWidget(self.request)
        widget.field = Choice(vocabulary=vocabulary.TreeVocabulary.fromDict({
            ('foo_group', 'Foo Group'): {
                ('bar_group', 'Bar Group'): {},
                ('qux_group', 'Qux Group'): {},
            },
            ('corge_group', 'Corge Group'): {
                ('grault_group', 'Grault Group'): {},
                ('garply_group', 'Garply Group'): {},
            },
        }))
        # Usse term.CollectionTermsVocabulary to simulate a named vocabulary
        # factory lookup
        widget.terms = term.CollectionTermsVocabulary(
            context=None, request=self.request, form=None, field=None,
            widget=widget, vocabulary=widget.field.vocabulary)
        widget.updateTerms()
        html = widget.render()
        self.assertNotIn(
            '<option value="foo_group">', html,
            'Top level vocab item rendered as <option...>')
        self.assertIn(
            '<optgroup label="Foo Group">', html,
            'Rendered select widget missing an <optgroup...>')

        base_args = widget._base_args()
        pattern_widget = widget._base(**base_args)
        items = pattern_widget.items
        self.assertIsInstance(
            items, dict,
            'Wrong widget items type')


class AjaxSelectWidgetTests(unittest.TestCase):

    layer = UNIT_TESTING
    maxDiff = None

    def setUp(self):
        self.request = TestRequest(environ={'HTTP_ACCEPT_LANGUAGE': 'en'})
        provideUtility(example_vocabulary_factory, name=u'example')

    def test_widget(self):
        from plone.app.z3cform.widget import AjaxSelectWidget
        widget = AjaxSelectWidget(self.request)
        widget.update()
        self.assertEqual(
            {
                'name': None,
                'value': u'',
                'pattern': 'select2',
                'pattern_options': {'separator': ';'},
            },
            widget._base_args(),
        )

        widget.vocabulary = 'example'
        self.assertEqual(
            widget._base_args(),
            {
                'name': None,
                'value': u'',
                'pattern': 'select2',
                'pattern_options': {
                    'vocabularyUrl': '/@@getVocabulary?name=example',
                    'separator': ';',
                },
            },
        )

        widget.value = 'token_three;token_two'
        self.assertDictEqual(
            {
                'name': None,
                'value': 'token_three;token_two',
                'pattern': 'select2',
                'pattern_options': {
                    'vocabularyUrl': '/@@getVocabulary?name=example',
                    'initialValues': {
                        'token_three': u'Three',
                        'token_two': u'Two',
                    },
                    'separator': ';',
                },
            },
            widget._base_args(),
        )

    def test_widget_list_orderable(self):
        from plone.app.z3cform.widget import AjaxSelectWidget
        widget = AjaxSelectWidget(self.request)
        widget.field = List(__name__='selectfield')
        self.assertEqual(
            {
                'name': None,
                'value': u'',
                'pattern': 'select2',
                'pattern_options': {'orderable': True, 'separator': ';'},
            },
            widget._base_args(),
        )

    def test_widget_tuple_orderable(self):
        from plone.app.z3cform.widget import AjaxSelectWidget
        widget = AjaxSelectWidget(self.request)
        widget.field = Tuple(__name__='selectfield')
        self.assertEqual(
            {
                'name': None,
                'value': u'',
                'pattern': 'select2',
                'pattern_options': {'orderable': True, 'separator': ';'},
            },
            widget._base_args(),
        )

    def test_widget_set_not_orderable(self):
        from plone.app.z3cform.widget import AjaxSelectWidget
        widget = AjaxSelectWidget(self.request)
        # A set is not orderable
        widget.field = Set(__name__='selectfield')
        self.assertEqual(
            {
                'name': None,
                'value': u'',
                'pattern': 'select2',
                'pattern_options': {'separator': ';'},
            },
            widget._base_args(),
        )

    def test_widget_choice(self):
        from plone.app.z3cform.widget import AjaxSelectWidget
        from zope.schema.interfaces import ISource
        widget = AjaxSelectWidget(self.request)
        source = Mock()
        alsoProvides(source, ISource)
        widget.field = Choice(__name__='choicefield', source=source)
        widget.name = 'choicefield'
        self.assertEqual(
            {
                'name': 'choicefield',
                'value': u'',
                'pattern': 'select2',
                'pattern_options': {
                    'separator': ';',
                    'maximumSelectionSize': 1,
                    'allowNewItems': 'false',
                    'vocabularyUrl':
                        'http://127.0.0.1/++widget++choicefield/@@getSource',
                },
            },
            widget._base_args(),
        )

    def test_widget_addform_url_on_addform(self):
        from plone.app.z3cform.widget import AjaxSelectWidget
        widget = AjaxSelectWidget(self.request)
        form = Mock(parentForm=None)
        from z3c.form.interfaces import IAddForm
        from zope.interface import directlyProvides  # noqa
        directlyProvides(form, IAddForm)  # noqa
        form.request = {'URL': 'http://addform_url'}
        widget.form = form
        self.assertEqual(
            {
                'name': None,
                'value': u'',
                'pattern': 'select2',
                'pattern_options': {'separator': ';'},
            },
            widget._base_args(),
        )
        widget.vocabulary = 'vocabulary1'
        self.assertEqual(
            {
                'name': None,
                'value': u'',
                'pattern': 'select2',
                'pattern_options': {
                    'separator': ';',
                    'vocabularyUrl':
                    'http://addform_url/@@getVocabulary?name=vocabulary1',
                },
            },
            widget._base_args(),
        )

    def test_data_converter_list(self):
        from plone.app.z3cform.converters import AjaxSelectWidgetConverter
        from plone.app.z3cform.widget import AjaxSelectWidget

        field = List(__name__='listfield', value_type=TextLine())
        widget = AjaxSelectWidget(self.request)
        widget.field = field
        converter = AjaxSelectWidgetConverter(field, widget)

        self.assertEqual(
            converter.toFieldValue(''),
            field.missing_value,
        )

        self.assertEqual(
            converter.toFieldValue('123;456;789'),
            ['123', '456', '789'],
        )

        self.assertEqual(
            converter.toWidgetValue([]),
            None,
        )

        self.assertEqual(
            converter.toWidgetValue(['123', '456', '789']),
            '123;456;789',
        )

    def test_data_converter_collection_with_vocabulary(self):
        from plone.app.z3cform.converters import AjaxSelectWidgetConverter
        from plone.app.z3cform.widget import AjaxSelectWidget

        field = Tuple(
            __name__='listfield',
            value_type=Choice(
                vocabulary='example',
            ),
        )
        widget = AjaxSelectWidget(self.request)
        widget.field = field
        converter = AjaxSelectWidgetConverter(field, widget)

        self.assertEqual(
            converter.toFieldValue(''),
            field.missing_value,
        )

        self.assertEqual(
            converter.toFieldValue('token_one;token_two;token_three'),
            ('one', 'two', 'three'),
        )

        self.assertEqual(
            converter.toWidgetValue([]),
            None,
        )

        self.assertEqual(
            converter.toWidgetValue(['123', '456', '789']),
            '123;456;789',
        )

    def test_data_converter_tuple(self):
        from plone.app.z3cform.converters import AjaxSelectWidgetConverter
        from plone.app.z3cform.widget import AjaxSelectWidget

        field = Tuple(__name__='tuplefield', value_type=TextLine())
        widget = AjaxSelectWidget(self.request)
        widget.field = field
        converter = AjaxSelectWidgetConverter(field, widget)

        self.assertEqual(
            converter.toFieldValue(''),
            field.missing_value,
        )

        self.assertEqual(
            converter.toFieldValue('123;456;789'),
            ('123', '456', '789'),
        )

        self.assertEqual(
            converter.toWidgetValue(tuple()),
            None,
        )

        self.assertEqual(
            converter.toWidgetValue(('123', '456', '789')),
            '123;456;789',
        )

    def test_fieldwidget(self):
        from plone.app.z3cform.widget import AjaxSelectFieldWidget
        from plone.app.z3cform.widget import AjaxSelectWidget
        field = Mock(__name__='field', title=u'', required=True)
        request = Mock()
        widget = AjaxSelectFieldWidget(field, request)
        self.assertTrue(isinstance(widget, AjaxSelectWidget))
        self.assertIs(widget.field, field)
        self.assertIs(widget.request, request)

    def test_fieldwidget_sequence(self):
        from plone.app.z3cform.widget import AjaxSelectFieldWidget
        from plone.app.z3cform.widget import AjaxSelectWidget
        field = Mock(__name__='field', title=u'', required=True)
        vocabulary = Mock()
        request = Mock()
        widget = AjaxSelectFieldWidget(field, vocabulary, request)
        self.assertTrue(isinstance(widget, AjaxSelectWidget))
        self.assertIs(widget.field, field)
        self.assertIs(widget.request, request)


class AjaxSelectWidgetIntegrationTests(unittest.TestCase):

    layer = PAZ3CForm_INTEGRATION_TESTING

    def setUp(self):
        self.request = TestRequest(environ={'HTTP_ACCEPT_LANGUAGE': 'en'})

    def test_keywords_can_add(self):
        from plone.app.z3cform.widget import AjaxSelectWidget

        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ['Manager'])
        widget = AjaxSelectWidget(self.request)
        widget.context = portal
        widget.vocabulary = 'plone.app.vocabularies.Keywords'
        self.assertEqual(
            widget._base_args()['pattern_options']['allowNewItems'],
            'true',
        )

    def test_keywords_cannot_add(self):
        from plone.app.z3cform.widget import AjaxSelectWidget

        portal = self.layer['portal']
        widget = AjaxSelectWidget(self.request)
        widget.context = portal
        widget.vocabulary = 'plone.app.vocabularies.Keywords'
        self.assertEqual(
            widget._base_args()['pattern_options']['allowNewItems'],
            'false',
        )


class QueryStringWidgetTests(unittest.TestCase):

    def setUp(self):
        self.request = TestRequest(environ={'HTTP_ACCEPT_LANGUAGE': 'en'})

    def test_converter_toWidgetValue(self):
        from plone.app.z3cform.converters import QueryStringDataConverter
        converter = QueryStringDataConverter(List(), None)
        self.assertEqual(converter.toWidgetValue(None), u'[]')
        self.assertEqual(converter.toWidgetValue([]), u'[]')

    def test_converter_empty_value(self):
        from plone.app.z3cform.converters import QueryStringDataConverter
        converter = QueryStringDataConverter(List(), None)
        self.assertEqual(converter.toFieldValue(u''), None)
        self.assertEqual(converter.toFieldValue(u'[]'), None)

    @mock.patch(
        'plone.app.widgets.utils.get_date_options',
        new=lambda *args, **kwargs: None,
    )
    @mock.patch(
        'plone.app.widgets.utils.get_relateditems_options',
        new=lambda *args, **kwargs: None,
    )
    def test_widget(self):
        from plone.app.z3cform.widget import QueryStringWidget
        widget = QueryStringWidget(self.request)
        self.assertEqual(
            {
                'name': None,
                'value': u'',
                'pattern': 'querystring',
                'pattern_options': {
                    'indexOptionsUrl': '/@@qsOptions',
                    'previewCountURL': '/@@querybuildernumberofresults',
                    'previewURL': '/@@querybuilder_html_results',
                    'patternAjaxSelectOptions': {'separator': ';'},
                    'patternDateOptions': None,
                    'patternRelateditemsOptions': None,
                },
            },
            widget._base_args(),
        )


class RelatedItemsWidgetIntegrationTests(unittest.TestCase):

    layer = PAZ3CForm_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = TestRequest(environ={'HTTP_ACCEPT_LANGUAGE': 'en'})
        setRequest(self.request)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def assertDictContainsSubsetReplacement(self, actual, expected):
        """assertDictContainsSubset was removed in Python 3.2, see:
        https://bugs.python.org/issue9424
        To not introduce a forward incompatibility, here is a replacement based
        on: http://stackoverflow.com/a/21058312
        """
        return set(expected.items()).issubset(set(actual.items()))

    def test_related_items_widget(self):
        from plone.app.z3cform.widget import RelatedItemsWidget
        EXPECTED_ROOT_PATH = '/plone'
        EXPECTED_ROOT_URL = 'http://nohost/plone'
        EXPECTED_BASE_PATH = '/plone'
        EXPECTED_VOCAB_URL = 'http://nohost/plone/@@getVocabulary?name=plone.app.vocabularies.Catalog'  # noqa

        widget = RelatedItemsWidget(self.request)
        widget.context = self.portal
        widget.update()

        result = widget._base_args()

        self.assertEqual(
            EXPECTED_ROOT_PATH,
            result['pattern_options']['rootPath'],
        )
        self.assertEqual(
            EXPECTED_ROOT_URL,
            result['pattern_options']['rootUrl'],
        )
        self.assertEqual(
            EXPECTED_BASE_PATH,
            result['pattern_options']['basePath'],
        )
        self.assertEqual(
            EXPECTED_VOCAB_URL,
            result['pattern_options']['vocabularyUrl'],
        )

    def test_related_items_widget_nav_root(self):
        from plone.app.layout.navigation.interfaces import INavigationRoot
        from plone.app.z3cform.widget import RelatedItemsWidget
        EXPECTED_ROOT_PATH = '/plone'
        EXPECTED_ROOT_URL = 'http://nohost/plone'
        EXPECTED_BASE_PATH = '/plone/subfolder'
        EXPECTED_VOCAB_URL = 'http://nohost/plone/@@getVocabulary?name=plone.app.vocabularies.Catalog'  # noqa

        self.portal.invokeFactory('Folder', 'subfolder')
        subfolder = self.portal['subfolder']
        alsoProvides(subfolder, INavigationRoot)

        widget = RelatedItemsWidget(self.request)
        widget.context = subfolder
        widget.update()
        result = widget._base_args()

        self.assertEqual(
            EXPECTED_ROOT_PATH,
            result['pattern_options']['rootPath'],
        )
        self.assertEqual(
            EXPECTED_ROOT_URL,
            result['pattern_options']['rootUrl'],
        )
        self.assertEqual(
            EXPECTED_BASE_PATH,
            result['pattern_options']['basePath'],
        )
        self.assertEqual(
            EXPECTED_VOCAB_URL,
            result['pattern_options']['vocabularyUrl'],
        )


class IRelationsType(Interface):
    single = RelationChoice(title=u'Single',
                            required=False, values=[])
    multiple = RelationList(title=u'Multiple (Relations field)',
                            required=False)


class RelatedItemsWidgetTemplateIntegrationTests(unittest.TestCase):

    layer = PAZ3CForm_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_related_items_widget_display_template(self):
        rel_fti = DexterityFTI(
            'RelationsType',
            schema=IRelationsType.__identifier__
        )
        self.portal.portal_types._setObject('RelationsType', rel_fti)

        intids = getUtility(IIntIds)

        self.portal.invokeFactory('RelationsType', 'source', title=u'A Source')
        self.portal.invokeFactory('RelationsType', 'target', title=u'A Target')
        self.portal.invokeFactory('Document', 'doc', title=u'A Document')
        source = self.portal['source']
        target = self.portal['target']
        doc = self.portal['doc']

        # Add some relations
        source.single = RelationValue(intids.getId(target))
        source.multiple = [RelationValue(intids.getId(target)), RelationValue(intids.getId(doc))]

        # Update relations
        from zope.event import notify
        from zope.lifecycleevent import ObjectModifiedEvent
        notify(ObjectModifiedEvent(source))
        default_view = source.restrictedTraverse('@@view')
        default_view.update()

        single = default_view.w['single']
        self.assertIsInstance(single, RelatedItemsWidget)
        self.assertTrue(single.value, target.UID())
        items = single.items()
        self.assertIsInstance(items, ContentListing)
        self.assertTrue(items[0].UID, target.UID())

        template = getMultiAdapter(
            (source, self.request, single.form, single.field, single),
            IPageTemplate, name=single.mode)
        self.assertTrue(template.filename.endswith('relateditems_display.pt'))
        html = template(single)
        self.assertIn('<span class="contenttype-relationstype state-missing-value url">A Target</span>', html)

        multiple = default_view.w['multiple']
        self.assertIsInstance(multiple, RelatedItemsWidget)
        self.assertTrue(multiple.value, ';'.join([target.UID(), doc.UID()]))
        items = multiple.items()
        self.assertIsInstance(items, ContentListing)
        self.assertTrue(items[0].UID, target.UID())
        self.assertTrue(items[1].UID, doc.UID())

        template = getMultiAdapter(
            (source, self.request, multiple.form, multiple.field, multiple),
            IPageTemplate, name=multiple.mode)
        self.assertTrue(template.filename.endswith('relateditems_display.pt'))
        html = template(multiple)
        self.assertIn('<span class="contenttype-relationstype state-missing-value url">A Target</span>', html)
        self.assertIn('<span class="contenttype-document state-missing-value url">A Document</span>', html)


class RelatedItemsWidgetTests(unittest.TestCase):

    def setUp(self):
        self.request = TestRequest(environ={'HTTP_ACCEPT_LANGUAGE': 'en'})

    @mock.patch(
        'plone.app.widgets.utils.getToolByName',
        new=Mock(return_value=Mock(return_value='testuser')),
    )
    def test_single_selection(self):
        """The pattern_options value for maximumSelectionSize should
        be 1 when the field only allows a single selection."""
        from plone.app.z3cform.widget import RelatedItemsFieldWidget
        context = Mock(absolute_url=lambda: 'fake_url',
                       getPhysicalPath=lambda: ['', 'site'])
        field = Choice(
            __name__='selectfield',
            values=['one', 'two', 'three'],
        )
        widget = RelatedItemsFieldWidget(field, self.request)
        widget.context = context
        widget.update()
        base_args = widget._base_args()
        pattern_options = base_args['pattern_options']
        self.assertEqual(pattern_options.get('maximumSelectionSize', 0), 1)

    @mock.patch(
        'plone.app.widgets.utils.getToolByName',
        new=Mock(return_value=Mock(return_value='testuser')),
    )
    def test_multiple_selection(self):
        """The pattern_options key maximumSelectionSize shouldn't be
        set when the field allows multiple selections"""
        from plone.app.z3cform.widget import RelatedItemsFieldWidget
        from zope.schema.interfaces import ISource
        from zope.schema.vocabulary import VocabularyRegistry

        context = Mock(absolute_url=lambda: 'fake_url',
                       getPhysicalPath=lambda: ['', 'site'])
        field = List(
            __name__='selectfield',
            value_type=Choice(vocabulary='foobar'),
        )
        widget = RelatedItemsFieldWidget(field, self.request)
        widget.context = context

        vocab = Mock()
        alsoProvides(vocab, ISource)
        with mock.patch.object(VocabularyRegistry, 'get', return_value=vocab):
            widget.update()
            base_args = widget._base_args()
        patterns_options = base_args['pattern_options']
        self.assertFalse('maximumSelectionSize' in patterns_options)
        self.assertEqual(
            patterns_options['vocabularyUrl'],
            '/@@getVocabulary?name=foobar&field=selectfield',
        )

    def test_converter_RelationChoice(self):
        from plone.app.z3cform.converters import RelationChoiceRelatedItemsWidgetConverter
        brain = Mock(getObject=Mock(return_value='obj'))
        portal_catalog = Mock(return_value=[brain])
        widget = Mock()
        converter = RelationChoiceRelatedItemsWidgetConverter(
            TextLine(),
            widget,
        )

        with mock.patch(
            'plone.app.z3cform.converters.IUUID',
            return_value='id',
        ):
            self.assertEqual(converter.toWidgetValue('obj'), 'id')
        self.assertEqual(converter.toWidgetValue(None), None)

        with mock.patch(
            'plone.app.z3cform.converters.getToolByName',
            return_value=portal_catalog,
        ):
            self.assertEqual(converter.toFieldValue('id'), 'obj')
        self.assertEqual(converter.toFieldValue(None), None)

    def test_converter_RelationList(self):
        from plone.app.z3cform.converters import RelatedItemsDataConverter
        from z3c.relationfield.interfaces import IRelationList
        field = List()
        alsoProvides(field, IRelationList)
        brain1 = Mock(getObject=Mock(return_value='obj1'), UID='id1')
        brain2 = Mock(getObject=Mock(return_value='obj2'), UID='id2')
        portal_catalog = Mock(return_value=[brain1, brain2])
        widget = Mock(separator=';')
        converter = RelatedItemsDataConverter(field, widget)

        self.assertEqual(converter.toWidgetValue(None), None)
        with mock.patch(
            'plone.app.z3cform.converters.IUUID',
            side_effect=['id1', 'id2'],
        ):
            self.assertEqual(
                converter.toWidgetValue(['obj1', 'obj2']),
                'id1;id2',
            )

        self.assertEqual(converter.toFieldValue(None), None)
        with mock.patch(
            'plone.app.z3cform.converters.getToolByName',
            return_value=portal_catalog,
        ):
            self.assertEqual(
                converter.toFieldValue('id1;id2'),
                ['obj1', 'obj2'],
            )

    def test_converter_List_of_Choice(self):
        from plone.app.z3cform.converters import RelatedItemsDataConverter
        fields = (
            List(),
            List(value_type=TextLine()),
            List(value_type=BytesLine()),
            List(value_type=Choice(values=['one', 'two', 'three'])),
        )
        for field in fields:
            expected_value_type = getattr(
                field.value_type,
                '_type',
                six.text_type,
            )
            if expected_value_type is None:
                expected_value_type = six.text_type
            widget = Mock(separator=';')
            converter = RelatedItemsDataConverter(field, widget)

            self.assertEqual(converter.toWidgetValue(None), None)
            self.assertEqual(
                converter.toWidgetValue(['id1', 'id2']),
                'id1;id2',
            )

            self.assertEqual(converter.toFieldValue(None), None)
            if not six.PY2 and expected_value_type == six.binary_type:
                expected = [b'id1', b'id2']
            else:
                expected = ['id1', 'id2']
            self.assertEqual(
                converter.toFieldValue('id1;id2'),
                expected,
            )

            self.assertEqual(converter.toFieldValue(None), None)
            self.assertEqual(
                type(converter.toFieldValue('id1;id2')[0]),
                expected_value_type,
            )

    def test_fieldwidget(self):
        from plone.app.z3cform.widget import RelatedItemsFieldWidget
        from plone.app.z3cform.widget import RelatedItemsWidget
        field = Mock(__name__='field', title=u'', required=True)
        vocabulary = Mock()
        request = Mock()
        widget = RelatedItemsFieldWidget(field, vocabulary, request)
        self.assertTrue(isinstance(widget, RelatedItemsWidget))
        self.assertIs(widget.field, field)
        self.assertIs(widget.request, request)


def add_mock_fti(portal):
    # Fake DX Type
    fti = DexterityFTI('dx_mock')
    portal.portal_types._setObject('dx_mock', fti)
    fti.klass = 'plone.dexterity.content.Item'
    fti.schema = 'plone.app.widgets.tests.test_dx.IMockSchema'
    fti.filter_content_types = False
    fti.behaviors = ('plone.app.dexterity.behaviors.metadata.IBasic',)


def _custom_field_widget(field, request):
    from plone.app.z3cform.widget import AjaxSelectWidget
    widget = FieldWidget(field, AjaxSelectWidget(request))
    widget.vocabulary = 'plone.app.vocabularies.PortalTypes'
    return widget


class RichTextWidgetTests(unittest.TestCase):

    layer = PAZ3CForm_INTEGRATION_TESTING

    def setUp(self):
        from plone.app.textfield import RichText as RichTextField

        self.portal = self.layer['portal']
        # since we are using a plone integration layer, we do
        # not need to use the TestRequest class and we do not want
        # to since the tinymce pattern requires a more properly
        # setup zope2 request object to work correctly in tests
        self.request = self.layer['request']

        class IWithText(Interface):
            text = RichTextField(title=u'Text')

        self.field = IWithText['text']

    def test_widget_params(self):
        from plone.app.z3cform.widget import RichTextWidget

        widget = FieldWidget(self.field, RichTextWidget(self.request))
        # set the context so we can get tinymce settings
        widget.context = self.portal
        widget.update()
        base_args = widget._base_args()
        self.assertEqual(base_args['name'], 'text')
        self.assertEqual(base_args['value'], u'')
        self.assertEqual(base_args['pattern'], 'tinymce')

        prependToUrl = '/plone/resolveuid/'
        self.assertEqual(
            base_args['pattern_options']['prependToUrl'],
            prependToUrl,
        )
        self.assertEqual(
            base_args['pattern_options']['upload']['relativePath'],
            '@@fileUpload',
        )

    def test_widget_params_different_contexts(self):
        from plone.app.z3cform.widget import RichTextWidget

        setRoles(self.portal, TEST_USER_ID, ['Contributor'])

        widget = FieldWidget(self.field, RichTextWidget(self.request))
        self.portal.invokeFactory('Folder', 'sub')
        sub = self.portal.sub
        form = Form(sub, self.request)

        # portal context
        widget.context = self.portal
        widget.update()
        base_args = widget._base_args()

        self.assertEqual(
            base_args['pattern_options']['relatedItems']['basePath'],
            '/plone',
        )

        # sub context
        widget.context = sub
        widget.update()
        base_args = widget._base_args()

        self.assertEqual(
            base_args['pattern_options']['relatedItems']['basePath'],
            '/plone/sub',
        )

        # form context
        widget.context = form
        widget.update()
        base_args = widget._base_args()

        self.assertEqual(
            base_args['pattern_options']['relatedItems']['basePath'],
            '/plone/sub',
        )

        # non-contentish context
        widget.context = None
        widget.update()
        base_args = widget._base_args()

        self.assertEqual(
            base_args['pattern_options']['relatedItems']['basePath'],
            '/plone',
        )

    def test_widget_values(self):
        from plone.app.textfield.value import RichTextValue
        from plone.app.z3cform.widget import RichTextWidget

        widget = FieldWidget(self.field, RichTextWidget(self.request))
        # set the context so we can get tinymce settings
        widget.context = self.portal
        widget.value = RichTextValue(u'Lorem ipsum \u2026')
        base_args = widget._base_args()
        self.assertEqual(base_args['value'], u'Lorem ipsum \u2026')

    def _set_mimetypes(self, default='text/html', allowed=('text/html')):
        """Set portal's mimetype settings.
        """
        if IMarkupSchema:
            registry = getUtility(IRegistry)
            self.settings = registry.forInterface(
                IMarkupSchema,
                prefix='plone',
            )
            self.settings.default_type = default
            self.settings.allowed_types = allowed

    def test_dx_tinymcewidget_single_mimetype(self):
        """A RichTextWidget with only one available mimetype should render the
        pattern class directly on itself.
        """
        if IMarkupSchema:
            # if not, don't run this test
            self._set_mimetypes(allowed=('text/html',))
            from plone.app.z3cform.widget import RichTextWidget
            widget = FieldWidget(self.field, RichTextWidget(self.request))
            # set the context so we can get tinymce settings
            widget.context = self.portal
            rendered = widget.render()

            self.assertTrue('<select' not in rendered)
            self.assertTrue('pat-tinymce' in rendered)
            self.assertTrue('data-pat-tinymce' in rendered)

    def test_dx_tinymcewidget_multiple_mimetypes_create(self):
        """A RichTextWidget with multiple available mimetypes should render a
        mimetype selection widget along with the textfield. When there is no
        field value, the default mimetype should be preselected.
        """
        if IMarkupSchema:
            # if not, don't run this test
            self._set_mimetypes(allowed=('text/html', 'text/plain'))
            from plone.app.z3cform.widget import RichTextWidget
            widget = FieldWidget(self.field, RichTextWidget(self.request))
            # set the context so we can get tinymce settings
            widget.context = self.portal
            rendered = widget.render()

            self.assertTrue('<select' in rendered)
            self.assertTrue('pat-textareamimetypeselector' in rendered)
            self.assertTrue('data-pat-textareamimetypeselector' in rendered)
            self.assertTrue(
                '<option value="text/html" selected="selected">' in rendered)
            self.assertTrue('pat-tinymce' not in rendered)

    def test_dx_tinymcewidget_multiple_mimetypes_edit(self):
        """A RichTextWidget with multiple available mimetypes should render a
        mimetype selection widget along with the textfield. When there is
        already a RichTextValue, it's mimetype should be preselected.
        """
        if IMarkupSchema:
            # if not, don't run this test
            self._set_mimetypes(allowed=('text/html', 'text/plain'))
            from plone.app.textfield.value import RichTextValue
            from plone.app.z3cform.widget import RichTextWidget
            widget = FieldWidget(self.field, RichTextWidget(self.request))
            # set the context so we can get tinymce settings
            widget.context = self.portal
            widget.value = RichTextValue(u'Hello world', mimeType='text/plain')
            rendered = widget.render()

            self.assertTrue('<select' in rendered)
            self.assertTrue('pat-textareamimetypeselector' in rendered)
            self.assertTrue('data-pat-textareamimetypeselector' in rendered)
            self.assertTrue(
                '<option value="text/plain" selected="selected">' in rendered,
            )
            self.assertTrue('pat-tinymce' not in rendered)

    def test_use_default_editor_value(self):
        """ Use dummy utility registered in testing.zcml """
        if IMarkupSchema:
            # if not, don't run this test
            self._set_mimetypes(allowed=('text/html',))
            registry = getUtility(IRegistry)
            from Products.CMFPlone.interfaces import IEditingSchema
            proxy = registry.forInterface(IEditingSchema, check=False,
                                            prefix='plone')
            proxy.available_editors = [u'dummy', u'TinyMCE']
            proxy.default_editor = u'dummy'
            from plone.app.z3cform.widget import RichTextWidget
            widget = FieldWidget(self.field, RichTextWidget(self.request))
            widget.context = self.portal
            rendered = widget.render()
            self.assertTrue('<p>dummy</p>' in rendered)

            proxy.default_editor = u'TinyMCE'
            from plone.app.z3cform.widget import RichTextWidget
            widget = FieldWidget(self.field, RichTextWidget(self.request))
            widget.context = self.portal
            rendered = widget.render()
            self.assertTrue('pat-tinymce' in rendered)


class LinkWidgetIntegrationTests(unittest.TestCase):

    layer = PAZ3CForm_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = TestRequest(environ={'HTTP_ACCEPT_LANGUAGE': 'en'})
        setRequest(self.request)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_link_widget__pattern_options(self):
        from plone.app.z3cform.widget import LinkWidget
        widget = LinkWidget(self.request)

        pattern_data = json.loads(widget.pattern_data())
        self.assertEqual(
            pattern_data['vocabularyUrl'],
            'http://nohost/plone/@@getVocabulary?name=plone.app.vocabularies.Catalog',  # noqa
        )
        self.assertEqual(pattern_data['maximumSelectionSize'], 1)

    def test_link_widget__extract_internal(self):
        from plone.app.z3cform.widget import LinkWidget
        widget = LinkWidget(self.request)
        widget.context = self.portal
        widget.name = 'testlinkwidget'
        widget.update()

        self.request.form['testlinkwidget.internal'] = 'abc'
        self.assertEqual(
            widget.extract(),
            u'${portal_url}/resolveuid/abc',
        )

    def test_link_widget__extract_external(self):
        from plone.app.z3cform.widget import LinkWidget
        widget = LinkWidget(self.request)
        widget.context = self.portal
        widget.name = 'testlinkwidget'
        widget.update()

        self.request.form['testlinkwidget.external'] = 'https://plone.org'
        self.assertEqual(
            widget.extract(),
            u'https://plone.org',
        )

    def test_link_widget__extract_email(self):
        from plone.app.z3cform.widget import LinkWidget
        widget = LinkWidget(self.request)
        widget.context = self.portal
        widget.name = 'testlinkwidget'
        widget.update()

        self.request.form['testlinkwidget.email'] = 'dev@plone.org'
        self.assertEqual(
            widget.extract(),
            u'mailto:dev@plone.org',
        )

    def test_link_widget__extract_email_including_mailto(self):
        from plone.app.z3cform.widget import LinkWidget
        widget = LinkWidget(self.request)
        widget.context = self.portal
        widget.name = 'testlinkwidget'
        widget.update()

        self.request.form['testlinkwidget.email'] = 'mailto:dev@plone.org'
        self.assertEqual(
            widget.extract(),
            u'mailto:dev@plone.org',
        )

    def test_link_widget__data_converter(self):
        from plone.app.z3cform.converters import LinkWidgetDataConverter
        from plone.app.z3cform.widget import LinkWidget

        field = TextLine(__name__='linkfield')
        widget = LinkWidget(self.request)
        converter = LinkWidgetDataConverter(field, widget)

        self.portal.invokeFactory('Folder', 'test')
        portal_url = self.portal.absolute_url()
        portal_path = '/'.join(self.portal.getPhysicalPath())

        # Test empty value
        widget_value = converter.toWidgetValue(u'')
        self.assertEqual(widget_value['internal'], u'')
        self.assertEqual(widget_value['external'], u'')
        self.assertEqual(widget_value['email'], u'')

        # Test external URLs
        self.assertEqual(
            converter.toWidgetValue(u'https://plone.org')['external'],
            u'https://plone.org',
        )

        # Test relative resolveuid URLs
        self.assertEqual(
            converter.toWidgetValue(u'/resolveuid/1234')['internal'],
            u'1234',
        )

        # Test absolute resolveuid URLs on the same domain
        self.assertEqual(
            converter.toWidgetValue(portal_url + '/resolveuid/1234')['internal'],  # noqa
            u'1234',
        )

        # Test absolute resolveuid URLs on a different domain
        self.assertEqual(
            converter.toWidgetValue(u'http://anyurl/resolveuid/1234')['external'],  # noqa
            u'http://anyurl/resolveuid/1234',
        )

        # Test interrnal URL paths
        self.assertEqual(
            converter.toWidgetValue(portal_path + '/test')['internal'],
            IUUID(self.portal.test),
        )

        # Test absolute interrnal URLs
        self.assertEqual(
            converter.toWidgetValue(portal_url + '/test')['internal'],
            IUUID(self.portal.test),
        )

        # Test mail
        self.assertEqual(
            converter.toWidgetValue(u'mailto:me')['email'],
            u'me',
        )

        # Test mail with subject
        self.assertEqual(
            converter.toWidgetValue(u'mailto:me?subject=jep')['email'],
            u'me',
        )
        self.assertEqual(
            converter.toWidgetValue(u'mailto:me?subject=jep')['email_subject'],
            u'jep',
        )


class WidgetCustomizingIntegrationTests(unittest.TestCase):

    layer = PAZ3CForm_INTEGRATION_TESTING

    def test_widget_base_wrapper_css(self):

        class ITestDateSchema(Schema):

            widget('my_date', DateWidget, wrapper_css_class='foo')
            my_date = Date(title=u'My Date')

        class TestForm(AutoExtensibleForm, EditForm):

            ignoreContext = True
            schema = ITestDateSchema

        render = TestForm(self.layer['portal'], self.layer['request'])
        self.assertIn(
            'empty foo" data-fieldname="form.widgets.my_date"',
            render(),
        )
