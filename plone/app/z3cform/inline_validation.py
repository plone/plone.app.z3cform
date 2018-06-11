# -*- coding: utf-8 -*-
from Acquisition import aq_base
from Products.CMFPlone.utils import normalizeString
from Products.Five import BrowserView
from zope.i18n import translate
from zope.i18nmessageid import Message

import json


class InlineValidationView(BrowserView):
    """Validate a form and return the error message for a particular field as JSON.
    """

    def __call__(self, fname=None, fset=None):
        self.request.response.setHeader('Content-Type', 'application/json')

        res = {'errmsg': ''}

        if fname is None:
            return json.dumps(res)

        try:
            form = aq_base(self.context).form_instance
        except AttributeError:
            form = self.context
        try:
            aq_base(form).update()
        except (AttributeError, TypeError):
            return json.dumps(res)

        if getattr(form, 'extractData', None):
            data, errors = form.extractData()
        else:
            return json.dumps(res)

        # if we validate a field in a group we operate on the group
        if fset is not None:
            try:
                fset = int(fset)  # integer-indexed fieldset names
                form = form.groups[fset]
            except (ValueError, TypeError):
                # try to match fieldset on group name
                def _name(group):
                    return getattr(group, '__name__', group.label)
                group_match = list(filter(
                    lambda group: normalizeString(_name(group)) == fset,
                    form.groups,
                ))
                if not group_match:
                    raise ValueError('Fieldset specified, but not found.')
                form = group_match[0]

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
        return json.dumps(res)
