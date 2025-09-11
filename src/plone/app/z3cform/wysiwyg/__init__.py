from zope.deferredimport import deprecated


# do not break plone.autoform
deprecated(
    "Use plone.app.z3cform.widgets.richtext.RichTextFieldWidget instead (will be removed in Plone 7)",
    WysiwygFieldWidget="plone.app.z3cform.widgets.richtext:RichTextFieldWidget",
)
