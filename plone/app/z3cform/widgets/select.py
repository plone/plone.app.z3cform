from OFS.interfaces import ISimpleItem
from plone.app.z3cform.interfaces import IAjaxSelectWidget
from plone.app.z3cform.interfaces import ISelect2Widget
from plone.app.z3cform.interfaces import ISelectWidget
from plone.app.z3cform.utils import dict_merge
from plone.app.z3cform.utils import get_context_url
from plone.app.z3cform.utils import get_widget_form
from plone.app.z3cform.widgets.base import HTMLInputWidget
from plone.app.z3cform.widgets.base import HTMLSelectWidget
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from z3c.form.browser.select import SelectWidget as SelectWidgetBase
from z3c.form.interfaces import IEditForm
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import IForm
from z3c.form.interfaces import ITerms
from z3c.form.interfaces import NO_VALUE
from z3c.form.widget import FieldWidget
from z3c.form.widget import Widget
from zope.component import getUtility
from zope.component import queryUtility
from zope.interface import implementer
from zope.interface import implementer_only
from zope.schema.interfaces import IChoice
from zope.schema.interfaces import ICollection
from zope.schema.interfaces import ISequence
from zope.schema.interfaces import ITreeVocabulary
from zope.schema.interfaces import IVocabularyFactory


@implementer_only(ISelectWidget)
class SelectWidget(HTMLSelectWidget, SelectWidgetBase):
    klass = "select-widget"


@implementer(IFieldWidget)
def SelectFieldWidget(field, request, extra=None):
    if extra is not None:
        request = extra
    return FieldWidget(field, SelectWidget(request))


@implementer(IFieldWidget)
def CollectionChoiceSelectFieldWidget(field, value_type, request):
    """IFieldWidget factory for SelectWidget."""
    return SelectFieldWidget(field, request)


@implementer_only(ISelect2Widget)
class Select2Widget(HTMLSelectWidget, SelectWidgetBase):
    """Select widget for z3c.form."""

    pattern = "select2"
    separator = ";"
    noValueToken = ""
    noValueMessage = ""
    orderable = False

    @property
    def items(self):
        """
        Optionally handle ITreeVocabulary vocabs as dicts.
        """
        terms = self.terms
        if ITerms.providedBy(terms):
            terms = terms.terms

        if ITreeVocabulary.providedBy(terms):
            groups = {}
            for group_term, option_terms in terms.items():
                group_widget = type(self)(self.request)
                group_widget.terms = option_terms
                group_widget.id = self.id
                group_label = group_term.title or group_term.value or group_term.token
                groups[group_label] = super(Select2Widget, group_widget).items
            return groups
        else:
            return super().items

    def get_pattern_options(self):
        pattern_options = {}

        # ISequence represents an orderable collection
        if ISequence.providedBy(self.field) or self.orderable:
            pattern_options["orderable"] = True

        if self.multiple:
            pattern_options["separator"] = self.separator

        # Allow to clear field value if it is not required
        if not self.field.required:
            pattern_options["allowClear"] = True

        return pattern_options

    def extract(self, default=NO_VALUE):
        """Override extract to handle delimited response values.
        Skip the vocabulary validation provided in the parent
        method, since it's not ever done for single selects."""
        if (
            self.name not in self.request
            and self.name + "-empty-marker" in self.request
        ):
            return []
        return self.request.get(self.name, default)


@implementer(IFieldWidget)
def Select2FieldWidget(field, request):
    return FieldWidget(field, Select2Widget(request))


@implementer_only(IAjaxSelectWidget)
class AjaxSelectWidget(HTMLInputWidget, Widget):
    """Ajax select widget for z3c.form."""

    pattern = "select2"
    separator = ";"
    vocabulary = None
    vocabulary_view = "@@getVocabulary"
    orderable = False

    def _view_context(self):
        view_context = get_widget_form(self)
        # For EditForms and non-Forms (in tests), the vocabulary is looked
        # up on the context, otherwise on the view
        if IEditForm.providedBy(view_context):
            if self.is_subform_widget():
                view_context = self.form.parentForm.context
            elif not ISimpleItem.providedBy(self.context):
                view_context = self.form.context
            else:
                view_context = self.context
        elif not IForm.providedBy(view_context):
            view_context = self.context
        return view_context

    def get_vocabulary(self):
        if self.vocabulary and isinstance(self.vocabulary, str):
            factory = queryUtility(
                IVocabularyFactory,
                self.vocabulary,
            )
            if factory:
                return factory(self._view_context())
        return self.vocabulary

    def display_items(self):
        if self.value:
            tokens = self.value.split(self.separator)
            vocabulary = self.get_vocabulary()
            for token in tokens:
                item = {"token": token, "title": token}
                if vocabulary is not None:
                    try:
                        item["title"] = vocabulary.getTermByToken(token).title
                    except LookupError:
                        pass
                yield item

    def has_multiple_values(self):
        return self.value and self.value.split(self.separator)

    def _ajaxselect_options(self):
        options = {
            "separator": self.separator,
        }
        if self.vocabulary:
            options["vocabularyUrl"] = "{}/{}?name={}".format(
                get_context_url(self._view_context()),
                self.vocabulary_view,
                self.vocabulary,
            )
            field_name = self.field and self.field.__name__ or None
            if field_name:
                options["vocabularyUrl"] += f"&field={field_name}"
            vocabulary = self.get_vocabulary()
            if vocabulary is not None and self.value:
                options["initialValues"] = dict()
                for token in self.value.split(self.separator):
                    try:
                        term = vocabulary.getTermByToken(token)
                        options["initialValues"][term.token] = term.title
                    except LookupError:
                        options["initialValues"][token] = token

        return options

    def update(self):
        super().update()
        field = getattr(self, "field", None)
        field = getattr(field, "value_type", field)
        if (
            not self.vocabulary
            and field is not None
            and getattr(field, "vocabularyName", None)
        ):
            self.vocabulary = field.vocabularyName

    def get_pattern_options(self):
        pattern_options = {}
        context = self.context
        field = None

        if IChoice.providedBy(self.field):
            pattern_options["maximumSelectionSize"] = 1
            field = self.field
        elif ICollection.providedBy(self.field):
            field = self.field.value_type
        if IChoice.providedBy(field):
            pattern_options["allowNewItems"] = "false"

        pattern_options = dict_merge(self._ajaxselect_options(), pattern_options)

        if field and getattr(field, "vocabulary", None):
            form_url = self.request.getURL()
            source_url = "{:s}/++widget++{:s}/@@getSource".format(
                form_url,
                self.name,
            )
            pattern_options["vocabularyUrl"] = source_url

        # ISequence represents an orderable collection
        if ISequence.providedBy(self.field) or self.orderable:
            pattern_options["orderable"] = True

        if self.vocabulary == "plone.app.vocabularies.Keywords":
            membership = getToolByName(context, "portal_membership")
            user = membership.getAuthenticatedMember()

            registry = getUtility(IRegistry)
            roles_allowed_to_add_keywords = registry.get(
                "plone.roles_allowed_to_add_keywords", set()
            )
            roles = set(user.getRolesInContext(context))
            allowNewItems = bool(
                roles.intersection(roles_allowed_to_add_keywords),
            )
            pattern_options["allowNewItems"] = str(
                allowNewItems,
            ).lower()

        return pattern_options


@implementer(IFieldWidget)
def AjaxSelectFieldWidget(field, request, extra=None):
    if extra is not None:
        request = extra
    return FieldWidget(field, AjaxSelectWidget(request))
