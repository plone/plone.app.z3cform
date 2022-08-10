from plone.z3cform.layout import FormWrapper
from z3c.form import button
from z3c.form import field
from z3c.form import form
from z3c.form import group
from z3c.form.contentprovider import ContentProviders
from z3c.form.interfaces import IFieldsAndContentProvidersForm
from zope import schema
from zope.contentprovider.provider import ContentProviderBase
from zope.interface import implementer
from zope.interface import Interface


class MySchema(Interface):
    age = schema.Int(title="Age")


class MyContentProvider(ContentProviderBase):
    def render(self):
        return "My test content provider"


@implementer(IFieldsAndContentProvidersForm)
class MyForm(form.Form):
    contentProviders = ContentProviders()
    contentProviders["myContentProvider"] = MyContentProvider
    # defining a contentProvider position is mandatory...
    contentProviders["myContentProvider"].position = 0
    label = "Please enter your age"
    ignoreContext = True  # don't use context to get widget data

    @button.buttonAndHandler("Apply")
    def handleApply(self, action):
        data, errors = self.extractData()


class MyFormWrapper(FormWrapper):
    form = MyForm


class MyGroupSchema(Interface):
    name = schema.TextLine(title="name")


class MyGroup(group.Group):
    label = "Secondary Group"
    __name__ = "MyGroup"
    fields = field.Fields(MyGroupSchema)


class MyGroupForm(group.GroupForm, form.Form):
    fields = field.Fields(MySchema)
    label = "Please enter your age and Name"
    ignoreContext = True  # don't use context to get widget data

    groups = [
        MyGroup,
    ]

    @button.buttonAndHandler("Apply")
    def handleApply(self, action):
        data, errors = self.extractData()


class MyGroupFormWrapper(FormWrapper):
    form = MyGroupForm


class MyMultiSchema(Interface):
    ages = schema.Dict(
        title="ages",
        key_type=schema.TextLine(title="name"),
        value_type=schema.Int(title="age", default=38),
    )


class MyMultiForm(form.Form):
    fields = field.Fields(MyMultiSchema)
    label = "Please enter the names and ages for each person"
    ignoreContext = True  # don't use context to get widget data

    @button.buttonAndHandler("Apply")
    def handleApply(self, action):
        data, errors = self.extractData()


class MyMultiFormWrapper(FormWrapper):
    form = MyMultiForm


def dummy_richtextwidget_render(widget):
    return "<p>dummy</p>"
