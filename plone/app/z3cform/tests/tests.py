from plone.app.z3cform.tests.layer import PAZ3CForm_INTEGRATION_TESTING
from plone.app.z3cform.tests.layer import PAZ3CForm_ROBOT_TESTING
from plone.browserlayer.layer import mark_layer
from plone.testing import layered
from zope.traversing.interfaces import BeforeTraverseEvent

import robotsuite
import unittest2 as unittest
import zope.component.testing
import zope.testing.doctest

ROBOT_TEST_LEVEL = 5


class IntegrationTests(unittest.TestCase):
    layer = PAZ3CForm_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        event = BeforeTraverseEvent(self.portal, self.request)
        mark_layer(self.portal, event)

    def test_layer_applied(self):
        from plone.app.z3cform.interfaces import IPloneFormLayer
        self.assertTrue(IPloneFormLayer.providedBy(self.portal.REQUEST))

    def test_default_templates(self):
        form = self.portal.restrictedTraverse('test-form')
        rendered = form()
        # look for something only in the Plone-specific @@ploneform-macros
        self.assertTrue('documentFirstHeading' in rendered)

    def test_content_provider(self):
        form = self.portal.restrictedTraverse('test-form')
        rendered = form()
        self.assertTrue('My test content provider' in rendered)


def test_suite():

    inlineValidationTests = zope.testing.doctest.DocFileSuite(
        'inline_validation.rst',
        package='plone.app.z3cform',
        optionflags=(
            zope.testing.doctest.ELLIPSIS |
            zope.testing.doctest.NORMALIZE_WHITESPACE
        )
    )
    inlineValidationTests.layer = PAZ3CForm_INTEGRATION_TESTING

    robotTests = layered(
        robotsuite.RobotTestSuite("test_multi.robot"),
        layer=PAZ3CForm_ROBOT_TESTING
    )
    suite = unittest.TestSuite([
        unittest.makeSuite(IntegrationTests),
        zope.testing.doctest.DocFileSuite(
            'wysiwyg/README.rst',
            package='plone.app.z3cform',
            setUp=zope.component.testing.setUp,
            tearDown=zope.component.testing.tearDown,
        ),
        zope.testing.doctest.DocFileSuite(
            'queryselect/README.rst',
            package='plone.app.z3cform',
            setUp=zope.component.testing.setUp,
            tearDown=zope.component.testing.tearDown,
        ),
        zope.testing.doctest.DocTestSuite(
            'plone.app.z3cform.wysiwyg.widget',
            package='plone.app.z3cform',
            setUp=zope.component.testing.setUp,
            tearDown=zope.component.testing.tearDown,
        ),
        inlineValidationTests,
        robotTests,
    ])
    return suite
