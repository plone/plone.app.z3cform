from plone.app.z3cform.interfaces import IQueryStringWidget
from plone.app.z3cform.utils import dict_merge
from plone.app.z3cform.utils import get_portal_url
from plone.app.z3cform.widgets.base import HTMLTextInputWidget
from plone.app.z3cform.widgets.datetime import get_date_options
from plone.app.z3cform.widgets.relateditems import get_relateditems_options
from z3c.form.interfaces import IFieldWidget
from z3c.form.widget import FieldWidget
from z3c.form.widget import Widget
from zope.globalrequest import getRequest
from zope.interface import implementer
from zope.interface import implementer_only


def get_querystring_options(context, querystring_view):
    portal_url = get_portal_url(context)
    try:
        base_url = context.absolute_url()
    except AttributeError:
        base_url = portal_url
    return {
        "indexOptionsUrl": f"{portal_url}/{querystring_view}",
        "previewURL": "%s/@@querybuilder_html_results" % base_url,
        "previewCountURL": "%s/@@querybuildernumberofresults" % base_url,
        "patternDateOptions": get_date_options(getRequest()),
        "patternAjaxSelectOptions": {"separator": ";"},
        "patternRelateditemsOptions": get_relateditems_options(
            context,
            None,
            ";",
            "plone.app.vocabularies.Catalog",
            "@@getVocabulary",
            "relatedItems",
            include_recently_added=False,
        ),
    }


@implementer_only(IQueryStringWidget)
class QueryStringWidget(HTMLTextInputWidget, Widget):
    """QueryString widget for z3c.form."""

    pattern = "querystring"
    querystring_view = "@@qsOptions"

    def get_pattern_options(self):
        """querystring pattern options"""
        return dict_merge(
            get_querystring_options(self.context, self.querystring_view),
            self.pattern_options,
        )


@implementer(IFieldWidget)
def QueryStringFieldWidget(field, request, extra=None):
    if extra is not None:
        request = extra
    return FieldWidget(field, QueryStringWidget(request))
