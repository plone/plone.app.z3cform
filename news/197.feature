Implement new `ContentBrowserWidget` for `pat-contentbrowser` pattern.

The deprecated `RelatedItemsWidget` and `pat-relateditems` pattern is still available
and imports should not break. But the default widget and converter adapter registration for
z3c.relationfield is changed to the new widget.

Since `plone.app.relationfield` defines the widget with `plone.autoform` schema
hints nothing changes until the package is updated to the new widget.
[petschki]
