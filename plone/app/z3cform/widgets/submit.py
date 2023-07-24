from plone.app.z3cform.interfaces import ISubmitWidget
from plone.app.z3cform.widgets.base import HTMLInputWidget
from z3c.form.button import ButtonAction as ButtonActionBase
from z3c.form.interfaces import IFieldWidget
from z3c.form.widget import FieldWidget
from z3c.form.widget import Widget
from zope.interface import implementer
from zope.interface import implementer_only


PRIMARY_BUTTON_NAMES = ("add", "save")


@implementer_only(ISubmitWidget)
class SubmitWidget(HTMLInputWidget, Widget):
    """submit widget"""

    klass = "submit-widget btn"

    @property
    def attributes(self):
        attributes = super().attributes
        if self.__name__ not in PRIMARY_BUTTON_NAMES:
            # do disable only primary buttons validation
            attributes["formnovalidate"] = True
        return attributes

    def update(self):
        if self.field.__name__ in PRIMARY_BUTTON_NAMES:
            self.addClass("btn-primary")
        else:
            self.addClass("btn-secondary")


@implementer(IFieldWidget)
def SubmitFieldWidget(field, request):
    submit = FieldWidget(field, SubmitWidget(request))
    submit.value = field.title
    return submit


class ButtonAction(SubmitWidget, ButtonActionBase):
    """need to subclass ButtonAction here
    to get our SubmitWidget adapter
    """
