import collective.testcaselayer.ptc
import zope.component.testing

from Products.Five import zcml
from Products.Five import fiveconfigure

class IntegrationTestLayer(collective.testcaselayer.ptc.BasePTCLayer):
    
    def afterSetUp(self):
        import plone.app.z3cform.tests
        
        fiveconfigure.debug_mode = True
        zcml.load_config('testing.zcml', plone.app.z3cform.tests)
        fiveconfigure.debug_mode = False
        
        self.addProfile('plone.app.z3cform:default')

class KSSUnitTestLayer(collective.testcaselayer.layer.Layer):
    
    def setUp(self):
        import plone.app.kss
        import plone.app.z3cform
        import kss.core.tests
        import z3c.form
        import Products.Five
        import Products.GenericSetup
        
        fiveconfigure.debug_mode = True
        
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
        
        fiveconfigure.debug_mode = False
    
    def tearDown(self):
        zope.component.testing.tearDown()
    
IntegrationLayer = IntegrationTestLayer([collective.testcaselayer.ptc.ptc_layer])
KSSLayer = KSSUnitTestLayer()
