from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

import plone.z3cform.layout

class FormWrapper(plone.z3cform.layout.FormWrapper):
    index = ViewPageTemplateFile('layout.pt')

def wrap_form(form, __wrapper_class=FormWrapper, **kwargs):
    return plone.z3cform.layout.wrap_form(form, __wrapper_class, **kwargs)
