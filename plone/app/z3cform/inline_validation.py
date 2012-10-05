import json

from Acquisition import aq_base
from Products.Five import BrowserView

from zope.i18nmessageid import Message
from zope.i18n import translate


class InlineValidationView(BrowserView):
    """Validate a form and return the error message for a particular field as JSON.
    """

    def __call__(self, fname, fset=None):
        res = {'errmsg': ''}

        form = self.context
        if hasattr(aq_base(form), 'form_instance'):
            form = form.form_instance
        if not hasattr(form, 'update'):
            return
        form.update()
        
        if getattr(form, "extractData", None):
            data, errors = form.extractData()
        else:
            return

        #if we validate a field in a group we operate on the group
        if fset is not None:
            fset = int(fset)
            form = form.groups[fset]

        index = len(form.prefix) + len(form.widgets.prefix)
        raw_fname = fname[index:]
        validationError = None
        for error in errors:
            if error.widget == form.widgets.get(raw_fname, None):
                validationError = error.message
                break

        if isinstance(validationError, Message):
            validationError = translate(validationError, context=self.request)

        res['errmsg'] = validationError or ''
        self.request.response.setHeader('Content-Type', 'application/json')
        return json.dumps(res)
