# -*- coding: utf-8 -*-
import os.path
import plone.app.z3cform
import plone.app.z3cform.interfaces
import plone.z3cform.interfaces
import plone.z3cform.templates
import z3c.form.interfaces

from Products.Five.browser import BrowserView
from Products.Five.browser.metaconfigure import ViewMixinForTemplates
from plone.dexterity.browser.add import DefaultAddForm
from plone.dexterity.browser.add import DefaultAddView
from plone.dexterity.browser.edit import DefaultEditForm
from plone.dexterity.interfaces import IDexterityEditForm
from plone.z3cform import layout
from z3c.form.error import ErrorViewTemplateFactory
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from zope.interface import classImplements


def path(filepart):
    return os.path.join(
        os.path.dirname(plone.app.z3cform.__file__),
        'templates',
        filepart,
    )

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


class RenderContentProvider(ViewMixinForTemplates, BrowserView):
    index = ViewPageTemplateFile('templates/contentprovider-widget.pt')


ErrorViewTemplate = ErrorViewTemplateFactory(
    os.path.join(os.path.dirname(__file__), 'templates/error.pt'),
    'text/html')


# Dexterity Add/Edit Form overrides
class BootstrapAddForm(DefaultAddForm):

    def updateActions(self):
        super(BootstrapAddForm, self).updateActions()
        if 'save' in self.actions:
            self.actions["save"].addClass("btn-primary")

        if 'cancel' in self.actions:
            self.actions["cancel"].ignoreRequiredOnValidation = True


class BootstrapAddView(DefaultAddView):
    form = BootstrapAddForm


class BootstrapEditForm(DefaultEditForm):

    def updateActions(self):
        super(BootstrapEditForm, self).updateActions()

        if 'save' in self.actions:
            self.actions["save"].addClass("btn-primary")

        if 'cancel' in self.actions:
            self.actions["cancel"].ignoreRequiredOnValidation = True


BootstrapEditView = layout.wrap_form(BootstrapEditForm)
classImplements(BootstrapEditView, IDexterityEditForm)
