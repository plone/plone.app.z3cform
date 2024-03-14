Add support for the "accept" attribute on file inputs.

If the widget's field - if there is one - has the "accept" attribute set (the
`NamedImage` field has `image/*` set by default) then this is rendered as an
`accept` attribute on the file input.

This would restrict the allowed file types before uploading while still being
checked on the server side.

Fixes: https://github.com/plone/plone.formwidget.namedfile/issues/66
Depends on:
- https://github.com/plone/plone.namedfile/pull/158
- https://github.com/plone/plone.formwidget.namedfile/pull/67
[thet]
