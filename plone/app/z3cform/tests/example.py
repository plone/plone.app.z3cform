# -*- coding: utf-8 -*-
from plone.z3cform.layout import FormWrapper
from z3c.form import button
from z3c.form import field
from z3c.form import form
from z3c.form import group
from z3c.form.contentprovider import ContentProviders
from z3c.form.interfaces import IFieldsAndContentProvidersForm
from zope import schema
from zope.contentprovider.provider import ContentProviderBase
from zope.interface import implementer
from zope.interface import Interface


class MySchema(Interface):
    age = schema.Int(title=u'Age')


class MyContentProvider(ContentProviderBase):

    def render(self):
        return 'My test content provider'


@implementer(IFieldsAndContentProvidersForm)
class MyForm(form.Form):
    contentProviders = ContentProviders()
    contentProviders['myContentProvider'] = MyContentProvider
    # defining a contentProvider position is mandatory...
    contentProviders['myContentProvider'].position = 0
    label = u'Please enter your age'
    ignoreContext = True  # don't use context to get widget data

    @button.buttonAndHandler(u'Apply')
    def handleApply(self, action):
        data, errors = self.extractData()


class MyFormWrapper(FormWrapper):
    form = MyForm


class MyGroupSchema(Interface):
    name = schema.TextLine(title=u'name')


class MyGroup(group.Group):
    label = u'Secondary Group'
    __name__ = u'MyGroup'
    fields = field.Fields(MyGroupSchema)


class MyGroupForm(group.GroupForm, form.Form):
    fields = field.Fields(MySchema)
    label = u'Please enter your age and Name'
    ignoreContext = True  # don't use context to get widget data

    groups = [MyGroup, ]

    @button.buttonAndHandler(u'Apply')
    def handleApply(self, action):
        data, errors = self.extractData()


class MyGroupFormWrapper(FormWrapper):
    form = MyGroupForm


class MyMultiSchema(Interface):
    ages = schema.Dict(title=u'ages',
                       key_type=schema.TextLine(title=u'name'),
                       value_type=schema.Int(title=u'age', default=38))


class MyMultiForm(form.Form):
    fields = field.Fields(MyMultiSchema)
    label = u'Please enter the names and ages for each person'
    ignoreContext = True  # don't use context to get widget data

    @button.buttonAndHandler(u'Apply')
    def handleApply(self, action):
        data, errors = self.extractData()


class MyMultiFormWrapper(FormWrapper):
    form = MyMultiForm


def dummy_richtextwidget_render(widget):
    return "<p>dummy</p>"
