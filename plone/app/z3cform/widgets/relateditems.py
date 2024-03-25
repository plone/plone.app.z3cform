from zope.deferredimport import deprecated as deprecated_import


deprecated_import(
    "plone.app.z3cform.widgets.relateditems is outdated and uses "
    "plone.app.z3cform.widgets.contenbrowser instead. You should "
    "consider updating your imports accordingly.",
    get_relateditems_options="plone.app.z3cform.widgets.contentbrowser:get_contentbrowser_options",
    RelatedItemsWidget="plone.app.z3cform.widgets.contentbrowser:ContentBrowserWidget",
    RelatedItemsFieldWidget="plone.app.z3cform.widgets.contentbrowser:ContentBrowserFieldWidget",
)
