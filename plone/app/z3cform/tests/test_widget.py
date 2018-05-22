# -*- coding: utf-8 -*-
from plone.app.z3cform.interfaces import IPloneFormLayer
from plone.app.z3cform.tests.layer import PAZ3CForm_INTEGRATION_TESTING
from plone.app.z3cform.wysiwyg.widget import WysiwygWidget
from zope import publisher
from zope.globalrequest import setRequest
from zope.interface import implementer

import unittest


@implementer(IPloneFormLayer)
class TestRequest(publisher.browser.TestRequest):
    pass


class TestForm(object):
    context = None


class NoAcquisitionAware(object):
    context = None
    request = TestRequest()


class TestWidget(unittest.TestCase):

    layer = PAZ3CForm_INTEGRATION_TESTING

    def setUp(self):
        self.request = TestRequest()
        setRequest(self.request)

    def test_missing_aq_chain(self):
        # testing support for contents witout Acquisiion chain (for avoid
        # regression)
        # See
        # https://github.com/plone/plone.app.z3cform/commit/587e229e267705a4fd48c6c51a76f849196fceba#commitcomment-2630299
        obj = NoAcquisitionAware()
        widget = WysiwygWidget(obj.request)
        widget.form = TestForm()
        widget.form.context = obj
        widget.update()
        self.assertTrue(hasattr(widget.form.context, 'aq_chain'))


def test_suite():
    return unittest.TestSuite([
        unittest.makeSuite(TestWidget),
    ])
