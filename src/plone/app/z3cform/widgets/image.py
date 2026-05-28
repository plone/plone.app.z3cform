from plone import api
from plone.formwidget.namedfile.widget import NamedImageWidget
from plone.namedfile.interfaces import INamedImageField
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import IFormLayer
from z3c.form.widget import FieldWidget
from zope.component import adapter
from zope.interface import implementer
from ZTUtils import make_query


class PortraitWidget(NamedImageWidget):
    # Cheat around 2 bugs:
    # * You are not authenticated during traversal, so fetching
    #   the current user does not work.
    # * download_url won't append our querystring, so fetching
    #   another user's image does not work.
    @property
    def download_url(self):
        userid = self.request.form.get("userid")
        if not userid:
            userid = api.user.get_current().getId()

        # anonymous
        if not userid:
            return None

        url = super().download_url
        if not url:
            return None

        return f"{url}?{make_query({'userid': userid})}"


@implementer(IFieldWidget)
@adapter(INamedImageField, IFormLayer)
def PortraitFieldWidget(field, request):
    return FieldWidget(field, PortraitWidget(request))
