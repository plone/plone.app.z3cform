import unittest

from zope.testing import doctest
from zope.component import testing

from Products.Five import zcml
from Products.Five import fiveconfigure
from Testing import ZopeTestCase as ztc
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

import plone.app.z3cform

@onsetup
def setUp():
    fiveconfigure.debug_mode = True
    zcml.load_config('configure.zcml', plone.app.z3cform)
    fiveconfigure.debug_mode = False
    ztc.installPackage('plone.app.z3cform')

setUp()
ptc.setupPloneSite()

def test_suite():
    return unittest.TestSuite([
        ztc.ZopeDocFileSuite('layout.txt', test_class=ptc.PloneTestCase),

        doctest.DocFileSuite(
           'wysiwyg/README.txt',
           setUp=testing.setUp, tearDown=testing.tearDown,
           ),

        doctest.DocFileSuite(
           'queryselect/README.txt',
           setUp=testing.setUp, tearDown=testing.tearDown,
           ),

        doctest.DocTestSuite(
           'plone.app.z3cform.wysiwyg.widget',
           setUp=testing.setUp, tearDown=testing.tearDown,
           ),
        ])
