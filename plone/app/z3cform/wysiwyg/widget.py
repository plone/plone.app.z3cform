import Acquisition
import zope.interface
import zope.schema.interfaces
from zope.app.component.hooks import getSite

import z3c.form.interfaces
import z3c.form.browser.textarea
import z3c.form.widget

class IWysiwygWidget(z3c.form.interfaces.ITextAreaWidget):
    pass

class WysiwygWidget(z3c.form.browser.textarea.TextAreaWidget):
    zope.interface.implementsOnly(IWysiwygWidget)
    
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
        if getattr(self.context, 'aq_inner', None) is None:
            self.context = Acquisition.ImplicitAcquisitionWrapper(
                self.context, getSite())

@zope.component.adapter(zope.schema.interfaces.IField,
                        z3c.form.interfaces.IFormLayer)
@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def WysiwygFieldWidget(field, request):
    """IFieldWidget factory for WysiwygWidget."""
    return z3c.form.widget.FieldWidget(field, WysiwygWidget(request))
