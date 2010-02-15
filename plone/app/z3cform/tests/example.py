from zope import interface, schema
from z3c.form import form, field, button, group
from plone.app.z3cform.layout import FormWrapper


class MySchema(interface.Interface):
    age = schema.Int(title=u"Age")


class MyForm(form.Form):
    fields = field.Fields(MySchema)
    label = u"Please enter your age"
    ignoreContext = True # don't use context to get widget data

    @button.buttonAndHandler(u'Apply')
    def handleApply(self, action):
        data, errors = self.extractData()


class MyFormWrapper(FormWrapper):
    form = MyForm


class MyGroupSchema(interface.Interface):
    name = schema.TextLine(title=u"name")


class MyGroup(group.Group):
    label = u'Secondary Group'
    fields = field.Fields(MyGroupSchema)

    
class MyGroupForm(group.GroupForm, form.Form):
    fields = field.Fields(MySchema)
    label = u"Please enter your age and Name"
    ignoreContext = True # don't use context to get widget data

    groups = [MyGroup, ]

    @button.buttonAndHandler(u'Apply')
    def handleApply(self, action):
        data, errors = self.extractData()


class MyGroupFormWrapper(FormWrapper):
    form = MyGroupForm

