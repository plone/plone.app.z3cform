Query select widget
===================

The ``plone.app.z3cform.queryselect`` module provides a query source
compatible with ``z3c.formwidget.query`` which combines to a selection field
that can be queried.

The native value type for the widget is Archetypes UID collections.
The default implementation will simply search using the
``SearchableText`` index in the portal catalog.

This is how your form schema could look like:

  >>> from zope import interface, schema
  >>> from plone.app.z3cform.queryselect import ArchetypesContentSourceBinder

  >>> class ISelection(interface.Interface):
  ...     items = schema.Set(
  ...         title=u"Selection",
  ...         description=u"Search for content",
  ...         value_type=schema.Choice(
  ...             source=ArchetypesContentSourceBinder()))

Optionally, instead of storing Archetypes UIDs, you can choose to use
``persistent.wref``, i.e. weak references, instead of UIDs:

  >>> from plone.app.z3cform.queryselect import uid2wref
  >>> factory = uid2wref(ISelection['items'])

To store weak references instead of UIDs you would register such a
factory as a component adapting the context.  The factory
automatically provides the interface which defines the field.
