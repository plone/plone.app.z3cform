import unittest
import zope.component.testing
import zope.testing.doctest

from plone.browserlayer.layer import mark_layer
from zope.traversing.interfaces import BeforeTraverseEvent

from Products.Five import zcml
from Products.PloneTestCase import ptc
from Products.PloneTestCase.layer import onsetup

from plone.app.z3cform.tests.layer import InlineValidationLayer, FUNCTIONAL_TESTS

from plone.testing import layered
import robotsuite



@onsetup
def setup_zcml():
    from Products.Five import fiveconfigure
    import plone.app.z3cform.tests
    fiveconfigure.debug_mode = True
    zcml.load_config('testing.zcml', plone.app.z3cform.tests)
    fiveconfigure.debug_mode = False

setup_zcml()
ptc.setupPloneSite(extension_profiles=('plone.app.z3cform:default',))


class IntegrationTests(ptc.PloneTestCase):

    def afterSetUp(self):
        import plone.app.z3cform.tests
        zcml.load_config('testing.zcml', plone.app.z3cform.tests)
        self.addProfile('plone.app.z3cform:default')
        event = BeforeTraverseEvent(self.portal, self.portal.REQUEST)
        mark_layer(self.portal, event)

    def test_layer_applied(self):
        from plone.app.z3cform.interfaces import IPloneFormLayer
        self.failUnless(IPloneFormLayer.providedBy(self.portal.REQUEST))

    def test_default_templates(self):
        form = self.portal.restrictedTraverse('test-form')
        rendered = form()
        # look for something only in the Plone-specific @@ploneform-macros
        self.failUnless('documentFirstHeading' in rendered)

    def test_content_provider(self):
        form = self.portal.restrictedTraverse('test-form')
        rendered = form()
        self.failUnless('My test content provider' in rendered)




def test_suite():

    inlineValidationTests = zope.testing.doctest.DocFileSuite('inline_validation.txt',
            package='plone.app.z3cform',
            optionflags=(zope.testing.doctest.ELLIPSIS | zope.testing.doctest.NORMALIZE_WHITESPACE)
        )

    inlineValidationTests.layer = InlineValidationLayer

    robotTests = layered(robotsuite.RobotTestSuite("test_multi.txt"),
            layer=FUNCTIONAL_TESTS)


    return unittest.TestSuite([
        unittest.makeSuite(IntegrationTests),

        zope.testing.doctest.DocFileSuite('wysiwyg/README.txt', package='plone.app.z3cform',
                setUp=zope.component.testing.setUp, tearDown=zope.component.testing.tearDown,
            ),

        zope.testing.doctest.DocFileSuite('queryselect/README.txt', package='plone.app.z3cform',
                setUp=zope.component.testing.setUp, tearDown=zope.component.testing.tearDown,
            ),

        zope.testing.doctest.DocTestSuite('plone.app.z3cform.wysiwyg.widget', package='plone.app.z3cform',
                setUp=zope.component.testing.setUp, tearDown=zope.component.testing.tearDown,
            ),

        inlineValidationTests,
        robotTests,

  ])
