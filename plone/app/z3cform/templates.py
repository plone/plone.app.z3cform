import os.path

import z3c.form.interfaces

import plone.z3cform.interfaces
import plone.z3cform.templates

import plone.app.z3cform
import plone.app.z3cform.interfaces

path = lambda p: os.path.join(os.path.dirname(plone.app.z3cform.__file__), 'templates', p)

# Override the layout wrapper view default template with a more Plone-looking
# one

layout_factory = plone.z3cform.templates.ZopeTwoFormTemplateFactory(
    path('layout.pt'),
    form=plone.z3cform.interfaces.IFormWrapper,
    request=plone.app.z3cform.interfaces.IPloneFormLayer)

# Override the form for the standard full-page form rendering

form_factory = plone.z3cform.templates.ZopeTwoFormTemplateFactory(
    path('form.pt'),
    form=z3c.form.interfaces.IForm,
    request=plone.app.z3cform.interfaces.IPloneFormLayer)
