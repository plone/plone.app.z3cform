from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

import plone.z3cform.layout


class FormWrapper(plone.z3cform.layout.FormWrapper):
    index = ViewPageTemplateFile('layout.pt')

    def render_form(self):
        """This method returns the rendered z3c.form form.

        Override this method if you need to pass a different context
        to your form, or if you need to render a number of forms.
        """
        form = self.form(self.context.aq_inner, self.request)
        form.__name__ = self.__name__
        return form()


def wrap_form(form, __wrapper_class=FormWrapper, **kwargs):
    return plone.z3cform.layout.wrap_form(form, __wrapper_class, **kwargs)
