from plone.app.z3cform.interfaces import ICheckBoxWidget
from plone.app.z3cform.widgets.base import HTMLInputWidget
from z3c.form.browser.checkbox import CheckBoxWidget as CheckBoxWidgetBase
from z3c.form.interfaces import IFieldWidget
from z3c.form.widget import FieldWidget
from zope.interface import implementer
from zope.interface import implementer_only


@implementer_only(ICheckBoxWidget)
class CheckBoxWidget(HTMLInputWidget, CheckBoxWidgetBase):
    """Implementation checkbox widget."""

    klass = "checkbox-widget"

    def update(self):
        super().update()
        if self.mode == "input":
            self.addClass("form-check-input")


@implementer(IFieldWidget)
def CheckBoxFieldWidget(field, request):
    return FieldWidget(field, CheckBoxWidget(request))
