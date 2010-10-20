
import z3c.form

from collective.z3cform.datetimewidget import widget_date
from collective.z3cform.datetimewidget import widget_datetime
from collective.z3cform.datetimewidget import widget_monthyear
from collective.z3cform.datetimewidget import interfaces


class IDateField(interfaces.IDateField):
    pass

class IDatetimeField(interfaces.IDatetimeField):
    pass



class DateWidget(widget_date.DateWidget):
    show_jquerytools_dateinput = True

class DatetimeWidget(widget_datetime.DatetimeWidget):
    show_jquerytools_dateinput = True

class MonthYearWidget(widget_monthyear.MonthYearWidget):
    show_jquerytools_dateinput = True



def DateFieldWidget(field, request):
    return z3c.form.widget.FieldWidget(field, DateWidget(request))

def DatetimeFieldWidget(field, request):
    return z3c.form.widget.FieldWidget(field, DatetimeWidget(request))

def MonthYearFieldWidget(field, request):
    return z3c.form.widget.FieldWidget(field, MonthYearWidget(request))


