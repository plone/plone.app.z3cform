import zope.app.pagetemplate.viewpagetemplatefile
import plone.z3cform.templates

class Macros(plone.z3cform.templates.Macros):
    template = zope.app.pagetemplate.viewpagetemplatefile.ViewPageTemplateFile(
        'macros.pt')
