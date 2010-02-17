WYSIWYG widget
==============

The ``plone.app.z3cform.wysiwyg`` package provides an implementation of the
Plone WYSIWYG widget compatible with ``z3c.form``.  This will allow you to
use Kupu, FCKeditor and other editors compatible with the Plone
WYSIWYG interface in your ``z3c.form`` forms.

To use, simply set the widget factory for the widget you'd like to be
displayed with the WYSIWYG widget:

  >>> from zope import interface, schema
  >>> from z3c.form import form, field
  >>> from z3c.form.interfaces import INPUT_MODE
  >>> from plone.app.z3cform.wysiwyg.widget import WysiwygFieldWidget

  >>> class IProfile(interface.Interface):
  ...     name = schema.TextLine(title=u"Name")
  ...     age = schema.Int(title=u"Age")
  ...     bio = schema.Text(title=u"Bio")

  >>> class MyForm(form.Form):
  ...     fields = field.Fields(IProfile)
  ...     fields['bio'].widgetFactory[INPUT_MODE] = WysiwygFieldWidget

