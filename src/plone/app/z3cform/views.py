from Products.Five.browser import BrowserView
from Products.Five.browser.metaconfigure import ViewMixinForTemplates
from z3c.form.error import ErrorViewTemplateFactory
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile

import os.path
import plone.app.z3cform
import plone.app.z3cform.interfaces
import plone.z3cform.interfaces
import plone.z3cform.templates
import z3c.form.interfaces


def path(filepart):
    return os.path.join(
        os.path.dirname(plone.app.z3cform.__file__),
        "templates",
        filepart,
    )


# Override the layout wrapper view default template with a more Plone-looking
# one


layout_factory = plone.z3cform.templates.ZopeTwoFormTemplateFactory(
    path("layout.pt"),
    form=plone.z3cform.interfaces.IFormWrapper,
    request=plone.app.z3cform.interfaces.IPloneFormLayer,
)

# Override the form for the standard full-page form rendering

form_factory = plone.z3cform.templates.ZopeTwoFormTemplateFactory(
    path("form.pt"),
    form=z3c.form.interfaces.IForm,
    request=plone.app.z3cform.interfaces.IPloneFormLayer,
)


# The ploneform-macros view
class Macros(BrowserView):
    def __getitem__(self, key):
        return self.index.macros[key]


# The widget rendering templates need to be Zope 3 templates
class RenderWidget(ViewMixinForTemplates, BrowserView):
    index = ViewPageTemplateFile("templates/widget.pt")


class RenderContentProvider(ViewMixinForTemplates, BrowserView):
    index = ViewPageTemplateFile("templates/contentprovider-widget.pt")


ErrorViewTemplate = ErrorViewTemplateFactory(
    os.path.join(os.path.dirname(__file__), "templates/error.pt"), "text/html"
)
