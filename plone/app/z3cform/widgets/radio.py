from plone.app.z3cform.interfaces import IRadioWidget
from plone.app.z3cform.widgets.base import HTMLInputWidget
from z3c.form.browser.radio import RadioWidget as RadioWidgetBase
from z3c.form.interfaces import IFieldWidget
from z3c.form.widget import FieldWidget
from zope.interface import implementer
from zope.interface import implementer_only


@implementer_only(IRadioWidget)
class RadioWidget(HTMLInputWidget, RadioWidgetBase):
    """Implementation of radio widget."""

    klass = "radio-widget"

    def update(self):
        super().update()
        if self.mode == "input":
            self.addClass("form-check-input")


@implementer(IFieldWidget)
def RadioFieldWidget(field, request):
    return FieldWidget(field, RadioWidget(request))
