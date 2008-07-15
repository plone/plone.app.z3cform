import os
import unittest

from zope.testing import doctest
from zope.component import testing
# from zope.app.testing.functional import ZCMLLayer

# testing_zcml_path = os.path.join(
#     os.path.dirname(__file__), 'testing.zcml')
# testing_zcml_layer = ZCMLLayer(
#     testing_zcml_path, 'plone.app.z3cform', 'testing_zcml_layer')

def test_suite():
    return unittest.TestSuite([
        doctest.DocFileSuite(
           'wysiwyg/README.txt',
           setUp=testing.setUp, tearDown=testing.tearDown,
           ),

        doctest.DocFileSuite(
           'queryselect/README.txt',
           setUp=testing.setUp, tearDown=testing.tearDown,
           ),

        doctest.DocTestSuite(
           'plone.z3cform.wysiwyg.widget',
           setUp=testing.setUp, tearDown=testing.tearDown,
           ),
        ])
