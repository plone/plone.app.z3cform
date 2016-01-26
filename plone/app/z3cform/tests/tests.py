from plone.app.z3cform.tests.layer import PAZ3CForm_INTEGRATION_TESTING
from plone.browserlayer.layer import mark_layer
from zope.traversing.interfaces import BeforeTraverseEvent

import doctest
import unittest
import zope.component.testing

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

    inlineValidationTests = doctest.DocFileSuite(
        'inline_validation.rst',
        package='plone.app.z3cform',
        optionflags=(
            doctest.ELLIPSIS |
            doctest.NORMALIZE_WHITESPACE
        )
    )
    inlineValidationTests.layer = PAZ3CForm_INTEGRATION_TESTING

    suite = unittest.TestSuite([
        unittest.makeSuite(IntegrationTests),
        doctest.DocFileSuite(
            'wysiwyg/README.rst',
            package='plone.app.z3cform',
            setUp=zope.component.testing.setUp,
            tearDown=zope.component.testing.tearDown,
        ),
        doctest.DocFileSuite(
            'queryselect/README.rst',
            package='plone.app.z3cform',
            setUp=zope.component.testing.setUp,
            tearDown=zope.component.testing.tearDown,
        ),
        doctest.DocTestSuite(
            'plone.app.z3cform.wysiwyg.widget',
            package='plone.app.z3cform',
            setUp=zope.component.testing.setUp,
            tearDown=zope.component.testing.tearDown,
        ),
        inlineValidationTests,
    ])
    return suite
