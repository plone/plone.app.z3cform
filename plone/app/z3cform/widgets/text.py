from plone.app.z3cform.interfaces import ITextAreaWidget
from plone.app.z3cform.interfaces import ITextLinesWidget
from plone.app.z3cform.interfaces import ITextWidget
from plone.app.z3cform.widgets.base import HTMLTextAreaWidget
from plone.app.z3cform.widgets.base import HTMLTextInputWidget
from z3c.form.interfaces import IFieldWidget
from z3c.form.widget import FieldWidget
from z3c.form.widget import Widget
from zope.interface import implementer
from zope.interface import implementer_only


@implementer_only(ITextWidget)
class TextWidget(HTMLTextInputWidget, Widget):
    """enhanced text widget"""

    klass = "text-widget"


@implementer(IFieldWidget)
def TextFieldWidget(field, request):
    return FieldWidget(field, TextWidget(request))


@implementer_only(ITextAreaWidget)
class TextAreaWidget(HTMLTextAreaWidget, Widget):
    """enhanced textarea widget"""

    klass = "textarea-widget"


@implementer(IFieldWidget)
def TextAreaFieldWidget(field, request):
    return FieldWidget(field, TextAreaWidget(request))


@implementer_only(ITextLinesWidget)
class TextLinesWidget(HTMLTextAreaWidget, Widget):
    """enhanced textarea widget"""

    klass = "textarea-widget"


@implementer(IFieldWidget)
def TextLinesFieldWidget(field, request):
    return FieldWidget(field, TextLinesWidget(request))


@implementer(IFieldWidget)
def TextLinesFieldWidgetFactory(field, value_type, request):
    return TextLinesFieldWidget(field, request)
