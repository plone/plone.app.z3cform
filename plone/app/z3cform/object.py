from plone.app.z3cform.utils import closest_content
from z3c.form.object import SubformAdapter as BaseSubformAdapter
from z3c.form.object import ObjectSubForm as BaseObjectSubForm


class ObjectSubForm(BaseObjectSubForm):

    def get_closest_content(self):
        """Return the closest persistent context to this form.
        The right context of this form is the object created by:
        z3c.form.object.registerFactoryAdapter
        """
        return closest_content(self.context)


class SubformAdapter(BaseSubformAdapter):
    """Subform factory adapter used to override the subform factory
    """
    factory = ObjectSubForm
