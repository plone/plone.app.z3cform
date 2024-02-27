from plone.app.z3cform.interfaces import IPasswordWidget
from plone.app.z3cform.widgets.base import HTMLTextInputWidget
from z3c.form.interfaces import IFieldWidget
from z3c.form.widget import FieldWidget
from z3c.form.widget import Widget
from zope.interface import implementer
from zope.interface import implementer_only


@implementer_only(IPasswordWidget)
class PasswordWidget(HTMLTextInputWidget, Widget):
    """enhanced text widget"""

    klass = "password-widget"


@implementer(IFieldWidget)
def PasswordFieldWidget(field, request):
    return FieldWidget(field, PasswordWidget(request))
