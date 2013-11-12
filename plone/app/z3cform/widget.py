from plone.app.widgets.dx import DateWidget  # TODO: move definition in here
from plone.app.widgets.dx import DatetimeWidget  # TODO: move def. in here
from zope.schema.interfaces import IDate
from zope.schema.interfaces import IDatetime
from z3c.form.widget import FieldWidget


class IDateField(IDate):
    pass


class IDatetimeField(IDatetime):
    pass


def DateFieldWidget(field, request):
    return FieldWidget(field, DateWidget(request))


def DatetimeFieldWidget(field, request):
    return FieldWidget(field, DatetimeWidget(request))
