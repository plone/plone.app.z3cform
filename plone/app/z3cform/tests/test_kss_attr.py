# -*- coding: utf-8 -*-
"""
plone.app.z3cform

Licensed under the GPL license, see LICENCE.txt for more details.

$Id$
"""
from Products.PloneTestCase import PloneTestCase as ptc
from kss.core.BeautifulSoup import BeautifulSoup
from Testing import ZopeTestCase as ztc
from Products.PloneTestCase.layer import PloneSite
from Products.Five.testbrowser import Browser
from Products.Five import zcml
import plone.app.z3cform


class TestKSSAttributes(ptc.FunctionalTestCase):
    BeautifulSoup = BeautifulSoup

    def afterSetUp(self):
        zcml.load_config('testing.zcml', plone.app.z3cform.tests)
        zcml.load_config('configure.zcml', plone.app.z3cform)
        self.user = ptc.default_user
        self.password = ptc.default_password
        self.browser = Browser()
        self.browser.handleErrors = False


def test_notLogged():
    r"""

    We create a simple z3c form.

        >>> self.browser.addHeader(
        ...    'Authorization', 'Basic %s:%s' % (self.user, self.password))
        >>> self.browser.open(self.folder.absolute_url() + '/test-form')
        >>> soup = self.BeautifulSoup(self.browser.contents)
        >>> print soup.find('div', 'form').prettify()

    """


def test_suite():
    suite = ztc.FunctionalDocTestSuite(test_class=TestKSSAttributes)
    suite.layer = PloneSite
    return suite
