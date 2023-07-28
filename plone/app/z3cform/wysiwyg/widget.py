from zope.deferredimport import deprecated


# do not break
deprecated(
    "Please refactor to plone.app.z3cform.widgets.richtext instead (will be removed in Plone 7)",
    IWysiwygWidget="plone.app.z3cform.interfaces:IRichTextWidget",
    WysiwygFieldWidget="plone.app.z3cform.widgets.richtext:RichTextFieldWidget",
    WysiwygWidget="plone.app.z3cform.widgets.richtext:RichTextWidget",
)
