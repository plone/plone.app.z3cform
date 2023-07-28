from zope.deferredimport import deprecated as deprecated_import


deprecated_import(
    "Import from plone.app.z3cform.converters instead (will be removed in Plone 7)",
    DatetimeWidgetConverter="plone.app.z3cform.converters:DatetimeWidgetConverter",
    DateWidgetConverter="plone.app.z3cform.converters:DateWidgetConverter",
)

deprecated_import(
    "Import from plone.app.z3cform.widgets.base instead (will be removed in Plone 7)",
    BaseWidget="plone.app.z3cform.widgets.base:BaseWidget",
)

deprecated_import(
    "Import from plone.app.z3cform.widgets.datetime instead (will be removed in Plone 7)",
    DateFieldWidget="plone.app.z3cform.widgets.datetime:DateFieldWidget",
    DatetimeFieldWidget="plone.app.z3cform.widgets.datetime:DatetimeFieldWidget",
    DatetimeWidget="plone.app.z3cform.widgets.datetime:DatetimeWidget",
    DateWidget="plone.app.z3cform.widgets.datetime:DateWidget",
    TimeFieldWidget="plone.app.z3cform.widgets.datetime:TimeFieldWidget",
    TimeWidget="plone.app.z3cform.widgets.datetime:TimeWidget",
)

deprecated_import(
    "Import from plone.app.z3cform.widgets.link instead (will be removed in Plone 7)",
    LinkFieldWidget="plone.app.z3cform.widgets.link:LinkFieldWidget",
    LinkWidget="plone.app.z3cform.widgets.link:LinkWidget",
)

deprecated_import(
    "Import from plone.app.z3cform.widgets.querystring instead (will be removed in Plone 7)",
    QueryStringFieldWidget="plone.app.z3cform.widgets.querystring:QueryStringFieldWidget",
    QueryStringWidget="plone.app.z3cform.widgets.querystring:QueryStringWidget",
)

deprecated_import(
    "Import from plone.app.z3cform.widgets.relateditems instead (will be removed in Plone 7)",
    RelatedItemsFieldWidget="plone.app.z3cform.widgets.relateditems:RelatedItemsFieldWidget",
    RelatedItemsWidget="plone.app.z3cform.widgets.relateditems:RelatedItemsWidget",
)

deprecated_import(
    "Import from plone.app.z3cform.widgets.richtext instead (will be removed in Plone 7)",
    RichTextFieldWidget="plone.app.z3cform.widgets.richtext:RichTextFieldWidget",
    RichTextWidget="plone.app.z3cform.widgets.richtext:RichTextWidget",
)

deprecated_import(
    "Import from plone.app.z3cform.widgets.select instead (will be removed in Plone 7)",
    AjaxSelectFieldWidget="plone.app.z3cform.widgets.select:AjaxSelectFieldWidget",
    AjaxSelectWidget="plone.app.z3cform.widgets.select:AjaxSelectWidget",
    SelectFieldWidget="plone.app.z3cform.widgets.select:Select2FieldWidget",
    SelectWidget="plone.app.z3cform.widgets.select:Select2Widget",
)

deprecated_import(
    "Import from plone.app.z3cform.widgets.singlecheckbox instead (will be removed in Plone 7)",
    SingleCheckBoxBoolFieldWidget="plone.app.z3cform.widgets.singlecheckbox:SingleCheckBoxBoolFieldWidget",
    SingleCheckBoxBoolWidget="plone.app.z3cform.widgets.singlecheckbox:SingleCheckBoxBoolWidget",
    SingleCheckBoxWidget="plone.app.z3cform.widgets.singlecheckbox:SingleCheckBoxWidget",
)
