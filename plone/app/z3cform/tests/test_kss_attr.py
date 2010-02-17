from Testing import ZopeTestCase as ztc
from Products.PloneTestCase import ptc
from Products.Five.testbrowser import Browser

from kss.core.BeautifulSoup import BeautifulSoup

from plone.app.z3cform.tests.layer import IntegrationLayer

class TestKSSAttributes(ptc.FunctionalTestCase):
    
    layer = IntegrationLayer
    
    BeautifulSoup = BeautifulSoup

    def afterSetUp(self):
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
        >>> div = soup.find('div', id="content-core")
        >>> form = div.form
        >>> 'kssattr-formname-test-form' in form['class']
        True

    Let's see if the name of a field is on its id:

        >>> soup.find('div', id='formfield-form-widgets-age') is not None
        True

    let's see if widget have the right class:

        >>> soup = self.BeautifulSoup(self.browser.contents)
        >>> soup.find('div',{'class':'field z3cformInlineValidation kssattr-fieldname-form.widgets.age'}) is not None
        True
    """

def test_group_form():
    r"""
        >>> self.browser.addHeader(
        ...    'Authorization', 'Basic %s:%s' % (self.user, self.password))
        >>> self.browser.open(self.folder.absolute_url() + '/test-group-form')

    Let's see if the kss-attr formname is actually on the form:

        >>> soup = self.BeautifulSoup(self.browser.contents)
        >>> div = soup.find('div', id="content-core")
        >>> form = div.form
        >>> 'kssattr-formname-test-group-form' in form['class']
        True

    Let's see that we have only one fieldset (we did not set 'show_default_label')...
    
        >>> fieldsets = soup.findAll('fieldset')
        >>> len(fieldsets) == 1
        True
        
        >>> group_fieldset = soup.find('fieldset', id='fieldset-0')
        >>> group_fieldset is not None
        True

    Let's see that the fieldset has the right kssattr

        >>> 'kssattr-fieldset-0' in group_fieldset['class']
        True

    ...and the fields have the right ids and only the name field is contained in
    the fieldset

        >>> soup.find('div', id='formfield-form-widgets-age') is not None
        True
        >>> group_fieldset.find('div', id='formfield-form-widgets-age') is not None
        False
        >>> name_field = group_fieldset.find('div', id='formfield-form-widgets-name')
        >>> name_field is not None
        True

    Let's see that the name field has the right kssattr

        >>> 'kssattr-fieldname-form.widgets.name' in name_field['class']
        True
        

    let's see if widget have the right class:

        >>> soup = self.BeautifulSoup(self.browser.contents)
        >>> soup.find('div',{'class':'field z3cformInlineValidation kssattr-fieldname-form.widgets.name'}) is not None
        True
    """

def test_suite():
    suite = ztc.FunctionalDocTestSuite(test_class=TestKSSAttributes)
    return suite
