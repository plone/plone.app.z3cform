# -*- coding: utf-8 -*-
"""
plone.app.z3cform

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl

$Id$
"""
from zope import interface, schema
from z3c.form import form, field, button
from plone.app.z3cform.layout import FormWrapper


class MySchema(interface.Interface):
    age = schema.Int(title=u"Age")


class MyForm(form.Form):
    fields = field.Fields(MySchema)
    ignoreContext = True # don't use context to get widget data

    @button.buttonAndHandler(u'Apply')
    def handleApply(self, action):
        data, errors = self.extractData()
        print data['age'] #     or do stuff


class MyFormWrapper(FormWrapper):
    form = MyForm
    label = u"Please enter your age"
