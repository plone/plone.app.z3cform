import os.path

from Products.Five.browser.metaconfigure import ViewMixinForTemplates
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile

import z3c.form.interfaces

import plone.z3cform.interfaces
import plone.z3cform.templates

import plone.app.z3cform
import plone.app.z3cform.interfaces

from Products.Five.browser import BrowserView

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


# The ploneform-macros view
class Macros(BrowserView):
    def __getitem__(self, key):
        return self.index.macros[key]


# The widget rendering templates need to be Zope 3 templates
class RenderWidget(ViewMixinForTemplates, BrowserView):
    index = ViewPageTemplateFile('templates/widget.pt')


class RenderSingleCheckboxWidget(ViewMixinForTemplates, BrowserView):
    index = ViewPageTemplateFile('templates/singlecheckbox.pt')


class RenderContentProvider(ViewMixinForTemplates, BrowserView):
    index = ViewPageTemplateFile('templates/contentprovider-widget.pt')
