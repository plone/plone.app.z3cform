import collective.testcaselayer.ptc
import zope.component.testing

from Products.Five import zcml
from Products.Five import fiveconfigure
from plone.app.testing import (
    PloneSandboxLayer,
    FunctionalTesting,
    PLONE_FIXTURE,
    TEST_USER_ID,
    TEST_USER_NAME,
    login,
    setRoles,
    applyProfile
)
from plone.testing import z2


class IntegrationTestLayer(collective.testcaselayer.ptc.BasePTCLayer):
    
    def afterSetUp(self):
        import plone.app.z3cform.tests
        
        fiveconfigure.debug_mode = True
        zcml.load_config('testing.zcml', plone.app.z3cform.tests)
        fiveconfigure.debug_mode = False
        
        self.addProfile('plone.app.z3cform:default')

class InlineValidationTestLayer(collective.testcaselayer.layer.Layer):
    
    def setUp(self):
        import plone.app.z3cform
        import z3c.form
        import Products.Five
        import Products.GenericSetup
        import Products.CMFCore
        import plone.i18n
        
        fiveconfigure.debug_mode = True
        
        zcml.load_config('meta.zcml', Products.GenericSetup)
        zcml.load_config('configure.zcml', Products.Five)
        zcml.load_config('configure.zcml', Products.CMFCore)
        zcml.load_config('configure.zcml', plone.i18n)

        zcml.load_config('meta.zcml', z3c.form)
        zcml.load_config('configure.zcml', z3c.form)

        zcml.load_config('configure.zcml', plone.app.z3cform)
        zcml.load_config('testing.zcml', plone.app.z3cform.tests)
        
        fiveconfigure.debug_mode = False
    
    def tearDown(self):
        zope.component.testing.tearDown()
    
IntegrationLayer = IntegrationTestLayer([collective.testcaselayer.ptc.ptc_layer])
InlineValidationLayer = InlineValidationTestLayer()

class FunctionalLayer(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Install product and call its initialize() function
        z2.installProduct(app, 'Products.Five')

        import plone.app.z3cform
        fiveconfigure.debug_mode = True
        self.loadZCML(name='testing.zcml', package=plone.app.z3cform.tests)
        fiveconfigure.debug_mode = False

    def setUpPloneSite(self, portal):
        pass

TEST_FIXTURE = FunctionalLayer()
FUNCTIONAL_TESTS = FunctionalTesting(
    bases=(TEST_FIXTURE, z2.ZSERVER_FIXTURE),
    name="plone.app.z3cform:Acceptance")
