from Acquisition import aq_inner
from Acquisition import aq_parent
from OFS.interfaces import IFolder
from OFS.interfaces import ISimpleItem
from plone.app.contentlisting.interfaces import IContentListing
from plone.app.z3cform.interfaces import IContentBrowserWidget
from plone.app.z3cform.utils import dict_merge
from plone.app.z3cform.utils import get_context_url
from plone.app.z3cform.utils import get_widget_form
from plone.app.z3cform.widgets.base import HTMLInputWidget
from plone.base import PloneMessageFactory as _
from plone.base.navigationroot import get_navigation_root_object
from plone.base.utils import get_top_site_from_url
from Products.CMFCore.utils import getToolByName
from z3c.form.interfaces import IEditForm
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import IForm
from z3c.form.widget import FieldWidget
from z3c.form.widget import Widget
from zope.component.hooks import getSite
from zope.globalrequest import getRequest
from zope.interface import implementer
from zope.interface import implementer_only
from zope.schema.interfaces import IChoice
from zope.schema.interfaces import ICollection


def get_contentbrowser_options(
    context,
    value,
    separator,
    vocabulary_name,
    vocabulary_view,
    field_name=None,
    include_recently_added=True,
):
    if IForm.providedBy(context):
        context = context.context

    request = getRequest()
    site = get_top_site_from_url(context, request)
    options = {
        "separator": separator,
    }
    if not vocabulary_name:
        # we need a vocabulary!
        raise ValueError("ContentBrowser needs a vocabulary")
    options["vocabularyUrl"] = "{}/{}?name={}".format(
        get_context_url(site),
        vocabulary_view,
        vocabulary_name,
    )
    if field_name:
        options["vocabularyUrl"] += f"&field={field_name}"
    if value:
        options["initialValues"] = {}
        catalog = False
        if vocabulary_name == "plone.app.vocabularies.Catalog":
            catalog = getToolByName(getSite(), "portal_catalog")
        for value in value.split(separator):
            title = value
            if catalog:
                result = catalog(UID=value)
                title = result[0].Title if result else value
            options["initialValues"][value] = title

    nav_root = get_navigation_root_object(context, site)

    if not ISimpleItem.providedBy(context):
        context = nav_root

    # basePath - start to search/browse in here.
    base_path_context = context
    if not IFolder.providedBy(base_path_context):
        base_path_context = aq_parent(aq_inner(base_path_context))
    if not base_path_context:
        base_path_context = nav_root
    options["basePath"] = "/".join(base_path_context.getPhysicalPath())

    # rootPath - Only display breadcrumb elements deeper than this path.
    options["rootPath"] = "/".join(site.getPhysicalPath()) if site else "/"

    # rootUrl: Visible URL up to the rootPath. This is prepended to the
    # currentPath to generate submission URLs.
    options["rootUrl"] = site.absolute_url() if site else ""

    # contextPath - current edited object. Will not be available to select.
    options["contextPath"] = "/".join(context.getPhysicalPath())

    if base_path_context != nav_root:
        options["favorites"] = [
            {
                "title": _("Current Content"),
                "path": "/".join(base_path_context.getPhysicalPath()),
            },
            {"title": _("Start Page"), "path": "/".join(nav_root.getPhysicalPath())},
        ]

    if include_recently_added:
        # Options for recently used key
        tool = getToolByName(context, "portal_membership")
        user = tool.getAuthenticatedMember()
        options["recentlyUsed"] = False  # Keep that off in Plone 5.1
        options["recentlyUsedKey"] = "contentbrowser_recentlyused_{}_{}".format(
            field_name or "", user.id
        )  # use string substitution with %s here for automatic str casting.

    return options


@implementer_only(IContentBrowserWidget)
class ContentBrowserWidget(HTMLInputWidget, Widget):
    """ContentBrowser widget for z3c.form."""

    pattern = "contentbrowser"
    separator = ";"
    vocabulary = None
    vocabulary_override = False
    vocabulary_view = "@@getVocabulary"
    orderable = False

    def update(self):
        super().update()
        field = getattr(self, "field", None)
        if ICollection.providedBy(self.field):
            field = self.field.value_type
        if (
            not self.vocabulary
            and field is not None
            and getattr(field, "vocabularyName", None)
        ):
            self.vocabulary = field.vocabularyName
            self.vocabulary_override = True
        else:
            self.vocabulary = "plone.app.vocabularies.Catalog"

    def get_pattern_options(self):
        field = None
        pattern_options = {}

        if IChoice.providedBy(self.field):
            pattern_options["maximumSelectionSize"] = 1
            field = self.field
        elif ICollection.providedBy(self.field):
            field = self.field.value_type

        vocabulary_name = self.vocabulary

        field_name = self.field and self.field.__name__ or None

        context = self.context
        view_context = get_widget_form(self)
        # For EditForms and non-Forms (in tests), the vocabulary is looked
        # up on the context, otherwise on the view
        if IEditForm.providedBy(view_context):
            if self.is_subform_widget():
                view_context = self.form.parentForm.context
            elif not ISimpleItem.providedBy(context):
                view_context = self.form.context
            else:
                view_context = context
        elif not IForm.providedBy(view_context):
            view_context = context
        else:
            pass
            # view_context is defined above already

        root_search_mode = (
            pattern_options.get("mode", None) and "basePath" not in pattern_options
        )

        pattern_options = dict_merge(
            get_contentbrowser_options(
                view_context,
                self.value,
                self.separator,
                vocabulary_name,
                self.vocabulary_view,
                field_name,
            ),
            pattern_options,
        )
        if root_search_mode:
            # Delete default basePath option in search mode, when no basePath
            # was explicitly set.
            del pattern_options["basePath"]
        if (
            not self.vocabulary_override
            and field
            and getattr(field, "vocabulary", None)
        ):
            # widget vocab takes precedence over field
            form_url = self.request.getURL()
            source_url = "{:s}/++widget++{:s}/@@getSource".format(
                form_url,
                self.name,
            )
            pattern_options["vocabularyUrl"] = source_url

        return pattern_options

    def items(self):
        """Return item for the widget values for the display template

        Query the catalog for the widget-value (uuids) to only display items
        that the user is allowed to see. Accessing the value with e.g.
        getattr(self.context, self.__name__) would yield the items unfiltered.
        Uses IContentListing for easy access to MimeTypeIcon and more.
        """
        results = []
        if not self.value:
            return results
        separator = getattr(self, "separator", ";")
        uuids = self.value.split(separator)

        try:
            catalog = getToolByName(self.context, "portal_catalog")
        except AttributeError:
            catalog = getToolByName(getSite(), "portal_catalog")

        brains = catalog(UID=uuids)
        # restore original order
        results = sorted(brains, key=lambda brain: uuids.index(brain.UID))
        return IContentListing(results)


@implementer(IFieldWidget)
def ContentBrowserFieldWidget(field, request, extra=None):
    if extra is not None:
        request = extra
    return FieldWidget(field, ContentBrowserWidget(request))
