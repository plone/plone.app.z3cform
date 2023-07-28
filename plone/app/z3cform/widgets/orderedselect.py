from plone.app.z3cform.interfaces import IOrderedSelectWidget
from plone.app.z3cform.widgets.base import HTMLSelectWidget
from z3c.form.browser.orderedselect import (
    OrderedSelectWidget as OrderedSelectWidgetBase,
)
from z3c.form.interfaces import IFieldWidget
from z3c.form.widget import FieldWidget
from zope.interface import implementer
from zope.interface import implementer_only


@implementer_only(IOrderedSelectWidget)
class OrderedSelectWidget(HTMLSelectWidget, OrderedSelectWidgetBase):
    """Implementation of radio widget."""

    klass = "radio-widget"


@implementer(IFieldWidget)
def OrderedSelectFieldWidget(field, request):
    return FieldWidget(field, OrderedSelectWidget(request))


@implementer(IFieldWidget)
def SequenceChoiceSelectFieldWidget(field, value_type, request):
    """IFieldWidget factory for SelectWidget."""
    return OrderedSelectFieldWidget(field, request)
