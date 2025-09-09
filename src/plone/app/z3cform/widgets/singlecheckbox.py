from plone.app.vocabularies.terms import TermWithDescription
from plone.app.z3cform.interfaces import IPloneFormLayer
from plone.app.z3cform.interfaces import ISingleCheckBoxBoolWidget
from plone.app.z3cform.widgets.base import HTMLInputWidget
from z3c.form.browser.checkbox import SingleCheckBoxWidget
from z3c.form.interfaces import IFieldWidget
from z3c.form.term import BoolTerms
from z3c.form.term import Terms
from z3c.form.widget import FieldWidget
from zope.component import adapter
from zope.interface import implementer
from zope.interface import implementer_only
from zope.schema.interfaces import IBool
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


@implementer_only(ISingleCheckBoxBoolWidget)
class SingleCheckBoxBoolWidget(HTMLInputWidget, SingleCheckBoxWidget):
    """Single Input type checkbox widget implementation."""

    klass = "single-checkbox-bool-widget"

    def update(self):
        super().update()
        if self.mode == "input":
            self.addClass("form-check-input")

    @property
    def label(self):
        if self.mode == "input":
            return ""
        return getattr(self, "_label", "")

    @label.setter
    def label(self, value):
        self._label = value

    @property
    def description(self):
        if self.mode == "input":
            return ""
        return getattr(self, "_description", "")

    @description.setter
    def description(self, value):
        self._description = value

    def updateTerms(self):
        if self.mode == "input":
            # in input mode use only one checkbox with true
            self.terms = Terms()
            self.terms.terms = SimpleVocabulary(
                (
                    TermWithDescription(
                        True,
                        "selected",
                        getattr(self, "_label", None) or self.field.title,
                        getattr(
                            self,
                            "_description",
                            None,
                        )
                        or self.field.description,
                    ),
                )
            )
            return self.terms
        if not self.terms:
            self.terms = Terms()
            self.terms.terms = SimpleVocabulary(
                [
                    SimpleTerm(*args)
                    for args in [
                        (True, "selected", BoolTerms.trueLabel),
                        (False, "unselected", BoolTerms.falseLabel),
                    ]
                ],
            )
        return self.terms

    @property
    def items(self):
        result = super().items
        for record in result:
            term = self.terms.terms.getTermByToken(record["value"])
            record["description"] = getattr(term, "description", "")
            record["required"] = self.required
        return result


@adapter(IBool, IPloneFormLayer)
@implementer(IFieldWidget)
def SingleCheckBoxBoolFieldWidget(field, request):
    """IFieldWidget factory for CheckBoxWidget."""
    return FieldWidget(field, SingleCheckBoxBoolWidget(request))
