from plone.app.event.base import default_timezone
from plone.app.z3cform.interfaces import IDatetimeWidget
from plone.app.z3cform.interfaces import IDateWidget
from plone.app.z3cform.interfaces import ITimeWidget
from plone.app.z3cform.utils import dict_merge
from plone.app.z3cform.widgets.base import HTMLTextInputWidget
from plone.base import PloneMessageFactory as _
from z3c.form.interfaces import IDataConverter
from z3c.form.interfaces import IFieldWidget
from z3c.form.widget import FieldWidget
from z3c.form.widget import Widget
from zope.component import getMultiAdapter
from zope.component.hooks import getSite
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


class DateTimeWidgetBase(HTMLTextInputWidget, Widget):
    _input_type = ""
    _formater = ""
    _formater_length = ""

    default_timezone = None
    default_time = "00:00:00"

    @property
    def attributes(self):
        attributes = super().attributes
        # NOTE: we're setting the "type" attribute here
        # which overrides 'type="text"' in templates/text_input.pt
        attributes["type"] = self._input_type
        return attributes

    def get_pattern_options(self):
        pat_options = dict_merge(
            get_date_options(self.request),
            self.pattern_options,
        )
        if self.field.required:
            pat_options["clear"] = False
        return pat_options

    def render(self):
        """Render widget.

        :returns: Widget's HTML.
        :rtype: string
        """
        if self.mode != "display":
            return super().render()

        if not self.value:
            return ""

        converter = getMultiAdapter((self.field, self), IDataConverter)

        if not converter:
            return self.value

        field_value = converter.toFieldValue(self.value)
        if field_value is self.field.missing_value:
            return ""

        formatter = self.request.locale.dates.getFormatter(
            self._formater,
            self._formater_length,
        )
        return formatter.format(field_value)


@implementer_only(IDateWidget)
class DateWidget(DateTimeWidgetBase):
    """Date widget for z3c.form."""

    _input_type = "date"
    _formater = "date"
    _formater_length = "short"

    pattern = "date-picker"
    klass = "date-widget"


@implementer(IFieldWidget)
def DateFieldWidget(field, request):
    return FieldWidget(field, DateWidget(request))


@implementer_only(IDatetimeWidget)
class DatetimeWidget(DateTimeWidgetBase):
    """Datetime widget for z3c.form."""

    _input_type = "datetime-local"
    _formater = "dateTime"
    _formater_length = "short"

    pattern = "datetime-picker"
    klass = "datetime-widget"

    @property
    def timezone(self):
        """Get the timezone for the datetime field or return the default
        timezone as timezone identifier string.

        :returns: Timezone identifier string.
        :rtype: string
        """
        try:
            # Case "Edit": Return the timezone of the original field's
            # datetime value, if available.
            original_value = self.field.get(self.context)

            if tzinfo := getattr(original_value, "tzinfo", None):
                return tzinfo.zone

        except AttributeError:
            # Case "Add" - no content object available yet.
            pass

        # Fall back the the portals or users timezone.
        return default_timezone()

    @property
    def timezone_vocabulary_url(self):
        return f"{getSite().absolute_url()}/@@getVocabulary?name=plone.app.vocabularies.Timezones"


@implementer(IFieldWidget)
def DatetimeFieldWidget(field, request):
    return FieldWidget(field, DatetimeWidget(request))


@implementer_only(ITimeWidget)
class TimeWidget(DateTimeWidgetBase):
    """TimeWidget for z3c.form."""

    _input_type = "time"
    _formater = "time"
    _formater_length = "short"
    klass = "time-widget"

    # no pattern set for time input
    pattern = ""


@implementer(IFieldWidget)
def TimeFieldWidget(field, request):
    return FieldWidget(field, TimeWidget(request))
