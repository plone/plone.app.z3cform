from datetime import date
from datetime import datetime
from datetime import time
from plone.app.z3cform import utils
from plone.app.z3cform.interfaces import IAjaxSelectWidget
from plone.app.z3cform.interfaces import IContentBrowserWidget
from plone.app.z3cform.interfaces import IDatetimeWidget
from plone.app.z3cform.interfaces import IDateWidget
from plone.app.z3cform.interfaces import ILinkWidget
from plone.app.z3cform.interfaces import IQueryStringWidget
from plone.app.z3cform.interfaces import IRelatedItemsWidget
from plone.app.z3cform.interfaces import ISelectWidget
from plone.app.z3cform.interfaces import ISingleCheckBoxBoolWidget
from plone.app.z3cform.interfaces import ITimeWidget
from plone.base.utils import safe_callable
from plone.uuid.interfaces import IUUID
from Products.CMFCore.utils import getToolByName
from z3c.form.converter import BaseDataConverter
from z3c.form.converter import CollectionSequenceDataConverter
from z3c.form.converter import SequenceDataConverter
from z3c.form.interfaces import ISequenceWidget
from z3c.relationfield.interfaces import IRelation
from z3c.relationfield.interfaces import IRelationList
from zope.component import adapter
from zope.component.hooks import getSite
from zope.schema.interfaces import IBool
from zope.schema.interfaces import ICollection
from zope.schema.interfaces import IDate
from zope.schema.interfaces import IDatetime
from zope.schema.interfaces import IField
from zope.schema.interfaces import IList
from zope.schema.interfaces import ITime

import json
import pytz
import urllib


@adapter(IDate, IDateWidget)
class DateWidgetConverter(BaseDataConverter):
    """Data converter for date fields."""

    def toWidgetValue(self, value):
        """Converts from field value to widget.

        :param value: Field value.
        :type value: date

        :returns: Date in format `Y-m-d`
        :rtype: string
        """
        if value is self.field.missing_value:
            return ""
        return ("{value.year:}-{value.month:02}-{value.day:02}").format(value=value)

    def toFieldValue(self, value):
        """Converts from widget value to field.

        :param value: Value inserted by date widget.
        :type value: string

        :returns: `date.date` object.
        :rtype: date
        """
        if not value:
            return self.field.missing_value
        return date(*map(int, value.split("-")))


@adapter(IDatetime, IDatetimeWidget)
class DatetimeWidgetConverter(BaseDataConverter):
    """Data converter for datetime fields."""

    def toWidgetValue(self, value):
        """Converts from field value to widget.

        :param value: Field value.
        :type value: datetime

        :returns: Datetime in format `Y-m-d H:M`
        :rtype: string
        """
        if value is self.field.missing_value:
            return ""
        return (
            f"{value.year:}-{value.month:02}-{value.day:02}T"
            f"{value.hour:02}:{value.minute:02}"
        )

    def toFieldValue(self, value):
        """Converts from widget value to field.

        :param value: Value inserted by datetime widget.
        :type value: string

        :returns: `datetime.datetime` object.
        :rtype: datetime
        """
        if not value:
            return self.field.missing_value
        tmp = value.split("T")
        if not tmp[0]:
            return self.field.missing_value
        value = tmp[0].split("-")
        if len(tmp) == 2 and ":" in tmp[1]:
            value += tmp[1].split(":")
        else:
            default_time = self.widget.default_time
            default_time = (
                default_time(self.widget.context)
                if safe_callable(default_time)
                else default_time
            )
            value += default_time.split(":")

        # TODO: respect the selected zone from the widget and just fall back
        # to default_zone
        default_zone = self.widget.default_timezone
        zone = (
            default_zone(self.widget.context)
            if safe_callable(default_zone)
            else default_zone
        )
        ret = datetime(*map(int, value))
        if zone:
            tzinfo = pytz.timezone(zone)
            ret = tzinfo.localize(ret)
        return ret


@adapter(IDatetime, IDateWidget)
class DateWidgetToDatetimeConverter(BaseDataConverter):
    """Data converter for date widget on datetime fields."""

    def toWidgetValue(self, value):
        """Converts from field value to widget.

        :param value: Field value.
        :type value: datetime

        :returns: Datetime in format `Y-m-d`
        :rtype: string
        """
        if value is self.field.missing_value:
            return ""
        return f"{value.year:}-{value.month:02}-{value.day:02}"

    def toFieldValue(self, value):
        """Converts from widget value to field.

        :param value: Value inserted by datetime widget.
        :type value: string

        :returns: `datetime.datetime` object.
        :rtype: datetime
        """
        if not value:
            return self.field.missing_value
        value = value.split("-")
        if len(value) != 3:
            return self.field.missing_value

        default_time = self.widget.default_time
        default_time = (
            default_time(self.widget.context)
            if safe_callable(default_time)
            else default_time
        )
        value += default_time.split(":")

        # TODO: respect the selected zone from the widget and just fall back
        # to default_zone
        default_zone = self.widget.default_timezone
        zone = (
            default_zone(self.widget.context)
            if safe_callable(default_zone)
            else default_zone
        )
        ret = datetime(*map(int, value))
        if zone:
            tzinfo = pytz.timezone(zone)
            ret = tzinfo.localize(ret)
        return ret


@adapter(ITime, ITimeWidget)
class TimeWidgetConverter(BaseDataConverter):
    """Data converter for datetime fields."""

    type = "time"

    def toWidgetValue(self, value):
        if value == self.field.missing_value:
            return ""
        return value.strftime("%H:%M")

    def toFieldValue(self, value):
        if value == "":
            return self.field.missing_value
        return time(*map(int, value.split(":")))


class Select2WidgetConverterBase:
    def toFieldValue(self, value):
        """Converts from widget value to field.

        :param value: Value inserted by Select2 widget or default html
                      select/multi-select
        :type value: string | list

        :returns: List of items
        :rtype: list | tuple | set
        """
        separator = getattr(self.widget, "separator", ";")
        if isinstance(value, str):
            value = value.strip()
            if value:
                value = value.split(separator)
            else:
                return self.field.missing_value
        elif value == ("",):
            return self.field.missing_value
        return super().toFieldValue(value)


@adapter(IField, ISelectWidget)
class SequenceSelect2WidgetConverter(
    Select2WidgetConverterBase,
    SequenceDataConverter,
):
    """Data converter for IField fields using the Select2Widget."""


@adapter(ICollection, ISelectWidget)
class Select2WidgetConverter(
    Select2WidgetConverterBase,
    CollectionSequenceDataConverter,
):
    """Data converter for ICollection fields using the Select2Widget."""


@adapter(ICollection, IAjaxSelectWidget)
class AjaxSelectWidgetConverter(BaseDataConverter):
    """Data converter for ICollection fields using the AjaxSelectWidget."""

    def toWidgetValue(self, value):
        """Converts from field value to widget tokenized widget value.

        :param value: Field value.
        :type value: list |tuple | set

        :returns: Items separated using separator defined on widget
        :rtype: string
        """
        if not value:
            return ""
        vocabulary = self.widget.get_vocabulary()
        tokenized_value = []
        for term_value in value:
            if vocabulary is not None:
                try:
                    term = vocabulary.getTerm(term_value)
                    tokenized_value.append(term.token)
                    continue
                except (LookupError, ValueError):
                    pass
            tokenized_value.append(str(term_value))
        return getattr(self.widget, "separator", ";").join(tokenized_value)

    def toFieldValue(self, value):
        """Converts from widget value to field.

        :param value: Value inserted by AjaxSelect widget.
        :type value: string

        :returns: List of items
        :rtype: list | tuple | set
        """
        collectionType = self.field._type
        if isinstance(collectionType, tuple):
            collectionType = collectionType[-1]
        if not len(value):
            return self.field.missing_value
        valueType = self.field.value_type._type
        if isinstance(valueType, tuple):
            valueType = valueType[0]
        separator = getattr(self.widget, "separator", ";")
        self.widget.update()  # needed to have a vocabulary
        vocabulary = self.widget.get_vocabulary()
        untokenized_value = []
        for token in value.split(separator):
            if vocabulary is not None:
                try:
                    term = vocabulary.getTermByToken(token)
                    if valueType:
                        untokenized_value.append(valueType(term.value))
                    else:
                        untokenized_value.append(term.value)
                    continue
                except (LookupError, ValueError):
                    pass
            untokenized_value.append(
                valueType(token) if valueType else token,
            )
        return collectionType(untokenized_value)


@adapter(IRelation, IContentBrowserWidget)
class RelationChoiceContentBrowserWidgetConverter(BaseDataConverter):
    """Data converter for RelationChoice fields using the ContentBrowserWidget."""

    def toWidgetValue(self, value):
        if not value:
            return self.field.missing_value
        return IUUID(value)

    def toFieldValue(self, value):
        if not value:
            return self.field.missing_value
        try:
            catalog = getToolByName(self.widget.context, "portal_catalog")
        except AttributeError:
            catalog = getToolByName(getSite(), "portal_catalog")

        res = catalog(UID=value)
        if res:
            return res[0].getObject()
        else:
            return self.field.missing_value


# BBB
@adapter(IRelation, IRelatedItemsWidget)
class RelationChoiceRelatedItemsWidgetConverter(
    RelationChoiceContentBrowserWidgetConverter
):
    """backwards compatibility"""


@adapter(IRelation, ISequenceWidget)
class RelationChoiceSelectWidgetConverter(RelationChoiceContentBrowserWidgetConverter):
    """Data converter for RelationChoice fields using with SequenceWidgets,
    which expect sequence values.
    """

    def toWidgetValue(self, value):
        if not value:
            missing = self.field.missing_value
            return [] if missing is None else missing
        return [IUUID(value)]


@adapter(ICollection, IContentBrowserWidget)
class ContentBrowserDataConverter(BaseDataConverter):
    """Data converter for ICollection fields using the ContentBrowserWidget."""

    def toWidgetValue(self, value):
        """Converts from field value to widget.

        :param value: List of catalog brains.
        :type value: list

        :returns: List of of UID separated by separator defined on widget.
        :rtype: string
        """
        if not value:
            return self.field.missing_value
        separator = getattr(self.widget, "separator", ";")
        if IRelationList.providedBy(self.field):
            return separator.join([IUUID(o) for o in value if o])
        else:
            return separator.join(v for v in value if v)

    def toFieldValue(self, value):
        """Converts from widget value to field.

        :param value: List of UID's separated by separator defined
        :type value: string

        :returns: List of content objects
        :rtype: list | tuple | set
        """
        if not value:
            return self.field.missing_value

        collectionType = self.field._type
        if isinstance(collectionType, tuple):
            collectionType = collectionType[-1]

        separator = getattr(self.widget, "separator", ";")
        # Some widgets (like checkbox) return lists
        if isinstance(value, str):
            value = value.split(separator)

        if IRelationList.providedBy(self.field):
            try:
                catalog = getToolByName(self.widget.context, "portal_catalog")
            except AttributeError:
                catalog = getToolByName(getSite(), "portal_catalog")

            objects = {
                item.UID: item.getObject() for item in catalog(UID=value) if item
            }

            return collectionType(
                objects[uid] for uid in value if uid in objects.keys()
            )
        else:
            valueType = getattr(self.field.value_type, "_type", str)
            if valueType is None:
                valueType = str
            if valueType == bytes:
                return collectionType(valueType(v, encoding="utf8") for v in value)
            return collectionType(valueType(v) for v in value)


# BBB
@adapter(ICollection, IRelatedItemsWidget)
class RelatedItemsDataConverter(ContentBrowserDataConverter):
    """backwards compatibility"""


@adapter(IRelationList, ISequenceWidget)
class RelationListSelectWidgetDataConverter(ContentBrowserDataConverter):
    """Data converter for RelationChoice fields using with SequenceWidgets,
    which expect sequence values.
    """

    def toWidgetValue(self, value):
        """Converts from field value to widget.

        :param value: List of catalog brains.
        :type value: list

        :returns: List of of UID.
        :rtype: list
        """
        if not value:
            missing = self.field.missing_value
            return [] if missing is None else missing
        if IRelationList.providedBy(self.field):
            return [IUUID(o) for o in value if o]
        else:
            return [v for v in value if v]


@adapter(IList, IQueryStringWidget)
class QueryStringDataConverter(BaseDataConverter):
    """Data converter for IList."""

    def toWidgetValue(self, value):
        """Converts from field value to widget.

        :param value: Query string.
        :type value: list

        :returns: Query string converted to JSON.
        :rtype: string
        """
        if not value:
            return "[]"
        return json.dumps(value)

    def toFieldValue(self, value):
        """Converts from widget value to field.

        :param value: Query string.
        :type value: string

        :returns: Query string.
        :rtype: list
        """
        try:
            value = json.loads(value)
        except ValueError:
            value = None
        if not value:
            return self.field.missing_value
        return value


@adapter(IField, ILinkWidget)
class LinkWidgetDataConverter(BaseDataConverter):
    """Data converter for the enhanced link widget."""

    def toWidgetValue(self, value):
        value = super().toWidgetValue(value)
        result = {
            "internal": "",
            "external": "",
            "email": "",
            "email_subject": "",
        }
        if not value:
            return result
        if value.startswith("mailto:"):
            # Handle mail URLs
            value = value[7:]  # strip mailto from beginning
            if "?subject=" in value:
                email, email_subject = value.split("?subject=")
                result["email"] = email
                result["email_subject"] = email_subject
            else:
                result["email"] = value
        else:
            uuid = None
            portal = getSite()
            is_same_domain = utils.is_same_domain(value, portal.absolute_url())
            is_absolute = utils.is_absolute(value)
            if "/resolveuid/" in value and (not is_absolute or is_same_domain):
                # Take the UUID part of a resolveuid url, but only if it's on
                # the same domain.
                uuid = value.rsplit("/", 1)[-1]
            elif not is_absolute or is_absolute and is_same_domain:
                # Handle relative URLs or absolute URLs on the same domain.
                parsed = urllib.parse.urlparse(value)
                if parsed.params or parsed.query or parsed.fragment:
                    # we don't want to loose query parameters
                    # so we don't convert URLs pointing to internal
                    # objects with params, queries or fragments
                    # to uids
                    pass
                else:
                    path = utils.replace_link_variables_by_paths(portal, parsed.path)
                    obj = portal.unrestrictedTraverse(path=path, default=None)
                    if obj is not None:
                        uuid = IUUID(obj, None)
            if uuid is not None:
                result["internal"] = uuid
            else:
                result["external"] = value
        return result

    def toFieldValue(self, value):
        """Converts from widget value to field."""

        if not value:
            return self.field.missing_value
        if isinstance(value, dict):
            internal = value.get("internal")
            external = value.get("external")
            email = value.get("email")
        else:
            return value
        if internal:
            url = "${portal_url}/resolveuid/" + internal
        elif email:
            subject = value.get("email_subject")
            if email[:7] != "mailto:":
                email = "mailto:" + email
            if not subject:
                url = email
            else:
                url = "{email}?subject={subject}".format(
                    email=email,
                    subject=subject,
                )
        else:
            url = external
        return url


@adapter(IBool, ISingleCheckBoxBoolWidget)
class BoolSingleCheckboxDataConverter(BaseDataConverter):
    """Special converter between boolean fields and single checkbox widgets."""

    def toWidgetValue(self, value):
        """Convert from Python bool to token sequence representation."""
        if value:
            return ["selected"]
        return ["unselected"]

    def toFieldValue(self, value):
        """See interfaces.IDataConverter"""
        # consider all different from true as false,
        # this way it works with one checkbox
        return bool(value and value[0] == "selected")
