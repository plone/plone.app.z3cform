from z3c.form.object import SubformAdapter as baseSubformAdapter
from z3c.form.object import ObjectSubForm as baseObjectSubForm

from utils import closest_content


class ObjectSubForm(baseObjectSubForm):

    def get_closest_content(self):
        """Return the closest persistent context to this form.
        The right context of this form is the object created by:
        z3c.form.object.registerFactoryAdapter
        """
        return closest_content(self.context)


class SubformAdapter(baseSubformAdapter):
    """Subform factory adapter used to override the subform factory
    """

    factory = ObjectSubForm
