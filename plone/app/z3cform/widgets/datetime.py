from plone.app.z3cform.converters import DatetimeWidgetConverter
from plone.app.z3cform.converters import DateWidgetConverter
from plone.app.z3cform.interfaces import IDatetimeWidget
from plone.app.z3cform.interfaces import IDateWidget
from plone.app.z3cform.interfaces import ITimeWidget
from plone.app.z3cform.utils import dict_merge
from plone.app.z3cform.widgets.base import BaseWidget
from plone.app.z3cform.widgets.patterns import InputWidget
from plone.base import PloneMessageFactory as _
from z3c.form.browser.text import TextWidget
from z3c.form.interfaces import IFieldWidget
from z3c.form.widget import FieldWidget
from zope.i18n import translate
from zope.interface import implementer
from zope.interface import implementer_only


def get_date_options(request):
    calendar = request.locale.dates.calendars["gregorian"]
    return {
        "behavior": "native",
        "week-numbers": "show",
        "first-day": calendar.week.get("firstDay") == 1 and 1 or 0,
        "today": translate(_("Today"), context=request),
        "clear": translate(_("Clear"), context=request),
    }


@implementer_only(IDateWidget)
class DateWidget(BaseWidget, TextWidget):
    """Date widget for z3c.form.

    :param default_timezone: A Olson DB/pytz timezone identifier or a callback
                             returning such an identifier.
    :type default_timezone: String or callback

    :param default_time: Time used by converter as fallback if no time was set in UI.
    :type default_time: String or callback

    The default_timezone and default_time arguments are only used if a datewidget is
    used on a datetime field. If used on a date field they are ignored.
    """

    _base_type = "date"
    _converter = DateWidgetConverter
    _formater = "date"
    _formater_length = "short"

    default_timezone = None
    default_time = "00:00:00"

    pattern = "date-picker"
    pattern_options = BaseWidget.pattern_options.copy()

    def _base(self, **kw):
        return InputWidget(
            type=self._base_type,
            **kw,
        )

    def _base_args(self):
        """Method which will calculate _base class arguments.

        Returns (as python dictionary):
            - `pattern`: pattern name
            - `pattern_options`: pattern options
            - `name`: field name
            - `value`: field value

        :returns: Arguments which will be passed to _base
        :rtype: dict
        """
        args = super()._base_args()
        args["name"] = self.name
        args["value"] = (self.request.get(self.name, self.value) or "").strip()

        args.setdefault("pattern_options", {})
        if self.field.required:
            # Required fields should not have a "Clear" button
            args["pattern_options"]["clear"] = False
        args["pattern_options"] = dict_merge(
            get_date_options(self.request), args["pattern_options"]
        )

        return args

    def render(self):
        """Render widget.

        :returns: Widget's HTML.
        :rtype: string
        """
        if self.mode != "display":
            self.addClass("form-control")
            return super().render()

        if not self.value:
            return ""

        field_value = self._converter(self.field, self).toFieldValue(self.value)
        if field_value is self.field.missing_value:
            return ""

        formatter = self.request.locale.dates.getFormatter(
            self._formater,
            self._formater_length,
        )
        return formatter.format(field_value)


@implementer(IFieldWidget)
def DateFieldWidget(field, request):
    return FieldWidget(field, DateWidget(request))


@implementer_only(IDatetimeWidget)
class DatetimeWidget(DateWidget):
    """Datetime widget for z3c.form.

    :param default_timezone: A Olson DB/pytz timezone identifier or a callback
                             returning such an identifier.
    :type default_timezone: String or callback

    :param default_time: Time used by converter as fallback if no time was set in UI.
    :type default_time: String or callback
    """

    _base_type = "datetime-local"
    _converter = DatetimeWidgetConverter
    _formater = "dateTime"

    default_timezone = None
    default_time = "00:00:00"

    pattern = "datetime-picker"


@implementer(IFieldWidget)
def DatetimeFieldWidget(field, request):
    return FieldWidget(field, DatetimeWidget(request))


@implementer_only(ITimeWidget)
class TimeWidget(BaseWidget, TextWidget):
    pattern = ""

    def _base(self, **kw):
        return InputWidget(
            type="time",
            name=self.name,
            value=(self.request.get(self.name, self.value) or "").strip(),
            **kw,
        )

    def render(self):
        if self.mode != "display":
            self.addClass("form-control")
        return super().render()


@implementer(IFieldWidget)
def TimeFieldWidget(field, request):
    return FieldWidget(field, TimeWidget(request))
