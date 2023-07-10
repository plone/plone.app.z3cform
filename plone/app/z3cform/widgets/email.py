from plone.app.z3cform.interfaces import IEmailWidget
from z3c.form.browser.text import TextWidget as z3cform_TextWidget
from z3c.form.interfaces import IFieldWidget
from z3c.form.widget import FieldWidget
from zope.interface import implementer
from zope.interface import implementer_only


@implementer_only(IEmailWidget)
class EmailWidget(z3cform_TextWidget):
    """Implementation of dumb email widget."""


@implementer(IFieldWidget)
def EmailFieldWidget(field, request):
    return FieldWidget(field, EmailWidget(request))
