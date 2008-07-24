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


def test_form():
    r"""

        >>> self.browser.addHeader(
        ...    'Authorization', 'Basic %s:%s' % (self.user, self.password))
        >>> self.browser.open(self.folder.absolute_url() + '/test-form')

    Let's see if the kss-attr formname is actually on the form:

        >>> soup = self.BeautifulSoup(self.browser.contents)
        >>> div = soup.find('div', 'form')
        >>> form = div.form
        >>> 'kssattr-formname-test-form' in form['class']
        True

    Let's see if the name of a field is on its id:

        >>> soup.find('div', id='formfield-form-widgets-age') is not None
        True

    let's see if widget have the right class:

        >>> soup = self.BeautifulSoup(self.browser.contents)
        >>> soup.find('div',{'class':'widget z3cformInlineValidation horizontal'}) is not None
        True
    """


def test_suite():
    suite = ztc.FunctionalDocTestSuite(test_class=TestKSSAttributes)
    suite.layer = PloneSite
    return suite
