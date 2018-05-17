# -*- coding: utf-8 -*-
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing.layers import IntegrationTesting
from plone.testing import z2


class PAZ3CFormLayer(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        z2.installProduct(app, 'Products.DateRecurringIndex')

        import plone.app.contenttypes
        self.loadZCML(package=plone.app.contenttypes,
                      context=configurationContext)

        import plone.app.z3cform
        self.loadZCML(package=plone.app.z3cform,
                      context=configurationContext)
        import plone.app.z3cform.tests
        self.loadZCML(name='testing.zcml',
                      package=plone.app.z3cform.tests,
                      context=configurationContext)

    def setUpPloneSite(self, portal):
        self.applyProfile(portal, 'plone.app.contenttypes:default')
        self.applyProfile(portal, 'plone.app.z3cform:default')


PAZ3CForm_FIXTURE = PAZ3CFormLayer()
PAZ3CForm_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PAZ3CForm_FIXTURE,),
    name='plone.app.z3cform:Integration',
)
