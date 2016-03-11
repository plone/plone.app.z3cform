# -*- coding: utf-8 -*-
from zope.component import adapter
from zope.component.hooks import getSite
from zope.interface import implementer
from zope.interface import implementer_only

import Acquisition
import logging
import z3c.form.browser.textarea
import z3c.form.interfaces
import z3c.form.widget
import zope.interface
import zope.schema.interfaces


logger = logging.getLogger('plone.app.z3cform')


class IWysiwygWidget(z3c.form.interfaces.ITextAreaWidget):
    pass


@implementer_only(IWysiwygWidget)
class WysiwygWidget(z3c.form.browser.textarea.TextAreaWidget):

    klass = u'kupu-widget'
    value = u''

    def update(self):
        super(z3c.form.browser.textarea.TextAreaWidget, self).update()
        z3c.form.browser.widget.addFieldClass(self)
        # We'll wrap context in the current site *if* it's not already
        # wrapped.  This allows the template to acquire tools with
        # ``context/portal_this`` if context is not wrapped already.
        # Any attempts to satisfy the Kupu template in a less idiotic
        # way failed:
        if getattr(self.form.context, 'aq_inner', None) is None:
            self.form.context = Acquisition.ImplicitAcquisitionWrapper(
                self.form.context, getSite())


@adapter(zope.schema.interfaces.IField, z3c.form.interfaces.IFormLayer)
@implementer(z3c.form.interfaces.IFieldWidget)
def WysiwygFieldWidget(field, request):
    """IFieldWidget factory for WysiwygWidget."""
    logger.warn(
        'plone.app.z3cform.wysiwyg.WysiwygFieldWidget is deprecated and'
        'will be removed in Plone 5.1',
        DeprecationWarning
    )
    return z3c.form.widget.FieldWidget(field, WysiwygWidget(request))
