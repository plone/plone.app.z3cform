from plone.app.z3cform.interfaces import IUriWidget
from plone.app.z3cform.widgets.text import TextWidget
from z3c.form.interfaces import IFieldWidget
from z3c.form.widget import FieldWidget
from zope.interface import implementer
from zope.interface import implementer_only


@implementer_only(IUriWidget)
class UriWidget(TextWidget):
    """Implementation of dumb URI widget."""

    klass = "uri-widget"

    @property
    def attributes(self):
        attributes = super().attributes
        # NOTE: we're setting the "type='url'" attribute here
        # which overrides 'type="text"' in templates/text_input.pt
        attributes["type"] = "url"
        return attributes


@implementer(IFieldWidget)
def UriFieldWidget(field, request):
    return FieldWidget(field, UriWidget(request))
