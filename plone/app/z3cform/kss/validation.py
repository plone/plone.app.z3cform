from Acquisition import aq_inner

from zope.interface import alsoProvides

from zope.i18nmessageid import Message
from zope.i18n import translate

from z3c.form.interfaces import IFormLayer

from plone.z3cform.interfaces import IFormWrapper
from plone.z3cform import z2

from plone.app.kss.plonekssview import PloneKSSView

from kss.core import kssaction


class Z3CFormValidation(PloneKSSView):
    """KSS actions for z3c form inline validation
    """

    @kssaction
    def validate_input(self, formname, fieldname, fieldset=None, value=None):
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
        
        form = request.traverseName(context, formname)
        if IFormWrapper.providedBy(form):
            formWrapper = form
            form = form.form_instance
            if not z2.IFixedUpRequest.providedBy(request):
                z2.switch_on(form, request_layer=formWrapper.request_layer)

        form.update()
        data, errors = form.extractData()

        #if we validate a field in a group we operate on the group
        if fieldset is not None:
            fieldset = int(fieldset)
            form = form.groups[fieldset]

        index = len(form.prefix) + len(form.widgets.prefix)
        raw_fieldname = fieldname[index:]
        validationError = None
        for error in errors:
            if error.widget == form.widgets.get(raw_fieldname, None):
                validationError = error.message
                break

        if isinstance(validationError, Message):
            validationError = translate(validationError, context=self.request)

        # Attempt to convert the value - this will trigge validation
        ksscore = self.getCommandSet('core')
        kssplone = self.getCommandSet('plone')
        validate_and_issue_message(ksscore, validationError, fieldname,
                                   fieldset, kssplone)


def validate_and_issue_message(ksscore, error, fieldname, fieldset,
                               kssplone=None):
    """A helper method also used by the inline editing view
    """
    if fieldset is not None:
        fieldId = '#fieldset-%s #formfield-%s' % (str(fieldset),
                                                  fieldname.replace('.', '-'))
        errorId = '#fieldset-%s #formfield-%s div.fieldErrorBox' % \
                                                 (str(fieldset),
                                                  fieldname.replace('.', '-'))
    else:
        fieldId = '#formfield-%s' % fieldname.replace('.', '-')
        errorId = '#formfield-%s div.fieldErrorBox' % fieldname.replace('.',
                                                                        '-')
    field_div = ksscore.getCssSelector(fieldId)
    error_box = ksscore.getCssSelector(errorId)

    if error:
        ksscore.replaceInnerHTML(error_box, error)
        ksscore.addClass(field_div, 'error')
    else:
        ksscore.clearChildNodes(error_box)
        ksscore.removeClass(field_div, 'error')
        if kssplone is not None:
            kssplone.issuePortalMessage('')

    return bool(error)
