from zope.component import getMultiAdapter

from kss.core import kssaction
from plone.app.kss.plonekssview import PloneKSSView
from zope.interface import alsoProvides
from z3c.form.interfaces import IFormLayer
from Acquisition import aq_inner

from plone.z3cform import z2


class Z3CFormValidation(PloneKSSView):
    """KSS actions for z3c form inline validation
    """

    @kssaction
    def validate_input(self, formname, fieldname, value=None):
        """Given a form (view) name, a field name and the submitted
        value, validate the given field.
        """

        # Abort if there was no value changed. Note that the actual value
        # comes along the submitted form, since a widget may require more than
        # a single form field to validate properly.
        if value is None:
            return

        context = aq_inner(self.context)
        request = aq_inner(self.request)
        alsoProvides(request, IFormLayer)

        # Find the form, the field and the widget
        formWrapper = getMultiAdapter((context, request), name=formname)
        form = formWrapper.form(context, request)
        if not hasattr(request, 'locale'): # we might already have a
                                           # zope.publisher request
            z2.switch_on(form, request_layer=formWrapper.request_layer)

        raw_fieldname = fieldname[len(form.prefix)+len('widgets.'):]

        form.update()
        data, errors = form.extractData()
        validationError = None
        for error in errors:
            if error.widget == form.widgets[raw_fieldname]:
                validationError = error.message
                break

        # Attempt to convert the value - this will trigge validation
        ksscore = self.getCommandSet('core')
        kssplone = self.getCommandSet('plone')
        validate_and_issue_message(ksscore, validationError, fieldname,
                                   kssplone)


def validate_and_issue_message(ksscore, error, fieldname, kssplone=None):
    """A helper method also used by the inline editing view
    """

    field_div = ksscore.getHtmlIdSelector('formfield-%s' % \
                                          fieldname.replace('.', '-'))
    error_box = ksscore.getCssSelector('#formfield-%s div.fieldErrorBox' % \
                                       fieldname.replace('.', '-'))

    if error:
        ksscore.replaceInnerHTML(error_box, error)
        ksscore.addClass(field_div, 'error')
    else:
        ksscore.clearChildNodes(error_box)
        ksscore.removeClass(field_div, 'error')
        if kssplone is not None:
            kssplone.issuePortalMessage('')

    return bool(error)
