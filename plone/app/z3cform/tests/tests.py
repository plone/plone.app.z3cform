import unittest

from zope.testing import doctest
from zope.component import testing

from Products.Five import zcml
from Products.Five import fiveconfigure
from Testing import ZopeTestCase as ztc
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

import plone.app.z3cform
import plone.app.kss
import kss.core.tests
import z3c.form
import Products.Five
import Products.GenericSetup


def kssTestSetUp(test):
    zcml.load_config('meta.zcml', Products.GenericSetup)
    zcml.load_config('configure.zcml', Products.Five)

    zcml.load_config('meta.zcml', kss.core)
    zcml.load_config('configure.zcml', kss.core)
    zcml.load_config('configure-unittest.zcml', kss.core.tests)
    zcml.load_config('configure.zcml', plone.app.kss)

    zcml.load_config('meta.zcml', z3c.form)
    zcml.load_config('configure.zcml', z3c.form)

    zcml.load_config('configure.zcml', plone.app.z3cform)
    zcml.load_config('testing.zcml', plone.app.z3cform.tests)


@onsetup
def setUp():
    fiveconfigure.debug_mode = True
    zcml.load_config('configure.zcml', plone.app.z3cform)
    zcml.load_config('configure-unittest.zcml', kss.core.tests)
    fiveconfigure.debug_mode = False

setUp()
ptc.setupPloneSite()


def test_suite():
    return unittest.TestSuite([
        ztc.ZopeDocFileSuite('layout.txt',
                             package='plone.app.z3cform',
                             test_class=ptc.PloneTestCase),

        doctest.DocFileSuite(
           'kss/README.txt',
           package='plone.app.z3cform',
           setUp=kssTestSetUp, tearDown=testing.tearDown,
            optionflags=(doctest.ELLIPSIS |
                         doctest.NORMALIZE_WHITESPACE)),

        doctest.DocFileSuite(
           'wysiwyg/README.txt',
           package='plone.app.z3cform',
           setUp=testing.setUp, tearDown=testing.tearDown,
           ),

        doctest.DocFileSuite(
           'queryselect/README.txt',
           package='plone.app.z3cform',
           setUp=testing.setUp, tearDown=testing.tearDown,
           ),

        doctest.DocTestSuite(
           'plone.app.z3cform.wysiwyg.widget',
           package='plone.app.z3cform',
           setUp=testing.setUp, tearDown=testing.tearDown,
           ),
        ])
