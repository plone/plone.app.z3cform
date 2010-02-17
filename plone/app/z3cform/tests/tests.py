import unittest
import zope.component.testing
import zope.testing.doctest

from plone.browserlayer.layer import mark_layer
from zope.app.publication.zopepublication import BeforeTraverseEvent

from Products.PloneTestCase import ptc
from Products.CMFCore.utils import getToolByName

from plone.app.z3cform.tests.layer import IntegrationLayer, KSSLayer

class IntegrationTests(ptc.PloneTestCase):
    layer = IntegrationLayer
    
    def afterSetUp(self):
        event = BeforeTraverseEvent(self.portal, self.portal.REQUEST)
        mark_layer(self.portal, event)
    
    def test_layer_applied(self):
        from plone.app.z3cform.interfaces import IPloneFormLayer
        self.failUnless(IPloneFormLayer.providedBy(self.portal.REQUEST))
    
    def test_kss_resource_installed(self):
        pk = getToolByName(self.portal, 'portal_kss')
        self.failUnless('++resource++plone.app.z3cform' in pk.getResourceIds())
    
    def test_default_templates(self):
        form = self.portal.restrictedTraverse('test-form')
        rendered = form()
        # look for something only in the Plone-specific @@ploneform-macros
        self.failUnless('documentFirstHeading' in rendered)

def test_suite():
    
    kssTests = zope.testing.doctest.DocFileSuite('kss/README.txt',
            package='plone.app.z3cform',
            optionflags=(zope.testing.doctest.ELLIPSIS | zope.testing.doctest.NORMALIZE_WHITESPACE)
        )
    kssTests.layer = KSSLayer
    
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
         
        kssTests,
          
        ])
