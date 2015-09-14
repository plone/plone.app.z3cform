from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.app.z3cform.interfaces import IPloneFormLayer
from plone.app.z3cform.tests.layer import PAZ3CForm_INTEGRATION_TESTING
from plone.app.z3cform.utils import closest_content
from z3c.form import form, field
from z3c.form.object import registerFactoryAdapter
from zope import interface, schema
from zope import publisher
from zope.globalrequest import setRequest

import unittest


class ISubObject(interface.Interface):

    title = schema.TextLine(
        title=u"Subobject Title"
    )


class SubObject(object):
    interface.implements(ISubObject)

    title = schema.fieldproperty.FieldProperty(ISubObject['title'])

    __name__ = ''
    __parent__ = None

    def getId(self):
        return self.__name__ or ''

    def __repr__(self):
        return "<SubObject title='%s'>" % self.title


registerFactoryAdapter(ISubObject, SubObject)


class IComplexForm(interface.Interface):

    object_field = schema.List(
        title=u"Object Field",
        required=False,
        value_type=schema.Object(
            title=u"object",
            schema=ISubObject
        )
    )


class ComplexForm(form.Form):
    fields = field.Fields(IComplexForm)
    label = u"Complex form"
    ignoreContext = True


class TestRequest(publisher.browser.TestRequest):
    interface.implements(IPloneFormLayer)


class TestObjectSubForm(unittest.TestCase):
    layer = PAZ3CForm_INTEGRATION_TESTING
    counter = 0

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = TestRequest()
        setRequest(self.request)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def _create_folder(self, fid):
        self.portal.invokeFactory('Folder', fid)
        return self.portal[fid]

    def test_closest_content(self):
        """Test the closest content utility directly
        """
        # without any information the closest content is Plone Site
        self.assertEqual(self.portal, closest_content())

        # we can pass a parameter to closest_content that will be
        # used to find a content object
        folder = self._create_folder('folder-1')
        self.assertEqual(folder, closest_content(folder))

    def test_multiwidget_subobjects(self):
        """Check the closest content of a MultiWidget subform
        """

        _form = ComplexForm(self.portal, self.request)
        _form.update()

        multi_wdgt = _form.widgets['object_field']
        multi_wdgt.appendAddingWidget()

        obj_wdgt = multi_wdgt.widgets[0]
        subform = obj_wdgt.subform

        # the context of the subform is None or a SubObject instance
        self.assertIsNone(subform.context, None)

        # now it's possbile to get a valid 'context'
        # by get_closest_content method
        self.assertEqual(
            subform.get_closest_content(),
            self.portal
        )

        # by changing the context of the main form the closest content
        # of its multiwidget subforms is the main form context itself
        folder = self._create_folder('folder-2')

        # XXX: in a real case the PUBLISHED attribute should be set by
        # ZPublisher
        self.request.PUBLISHED = folder

        _form = ComplexForm(folder, self.request)
        _form.update()

        multi_wdgt = _form.widgets['object_field']
        multi_wdgt.appendAddingWidget()

        obj_wdgt = multi_wdgt.widgets[0]
        subform = obj_wdgt.subform

        # now the closest content is the folder
        self.assertEqual(
            subform.get_closest_content(),
            folder
        )


def test_suite():

    return unittest.TestSuite([
        unittest.makeSuite(TestObjectSubForm),
    ])
