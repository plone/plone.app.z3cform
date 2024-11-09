from plone.app.z3cform.interfaces import ILinkWidget
from plone.app.z3cform.widgets.base import HTMLTextInputWidget
from plone.base.utils import safe_text
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import NO_VALUE
from z3c.form.widget import FieldWidget
from z3c.form.widget import Widget
from zope.component.hooks import getSite
from zope.interface import implementer
from zope.interface import implementer_only

import json


@implementer_only(ILinkWidget)
class LinkWidget(HTMLTextInputWidget, Widget):
    """Implementation of enhanced link widget.

    .. note::
        Unlike the others here, this is not a pattern based widget
        and it uses it's own template.
    """

    def pattern_data(self):
        context = self.context or getSite()
        pattern_data = {
            "vocabularyUrl": "{}/@@getVocabulary?name=plone.app.vocabularies.Catalog".format(  # noqa
                getSite().absolute_url(0),
            ),
            "rootPath": "/".join(getSite().getPhysicalPath()),
            "basePath": "/".join(context.getPhysicalPath()),
            "maximumSelectionSize": 1,
        }
        return json.dumps(pattern_data)

    def extract(self, default=NO_VALUE):
        form = self.request.form
        internal = form.get(self.name + ".internal")
        external = form.get(self.name + ".external")
        email = form.get(self.name + ".email")
        if internal:
            url = "${portal_url}/resolveuid/" + internal
        elif email:
            subject = form.get(self.name + ".subject")
            if email[:7] != "mailto:":
                email = "mailto:" + email
            if not subject:
                url = email
            else:
                url = "{email}?subject={subject}".format(
                    email=email,
                    subject=subject,
                )
        else:
            url = external  # the default is `http://` so we land here
        if url:
            self.request.form[self.name] = safe_text(url)
        return super().extract(default=default)


@implementer(IFieldWidget)
def LinkFieldWidget(field, request):
    return FieldWidget(field, LinkWidget(request))
