from OFS.interfaces import ISimpleItem
from plone.app.z3cform.interfaces import IAjaxSelectWidget
from plone.app.z3cform.interfaces import ISelectWidget
from plone.app.z3cform.utils import dict_merge
from plone.app.z3cform.utils import get_context_url
from plone.app.z3cform.utils import get_widget_form
from plone.app.z3cform.widgets.base import BaseWidget
from plone.app.z3cform.widgets.patterns import InputWidget
from plone.app.z3cform.widgets.patterns import SelectWidget
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from z3c.form import interfaces as form_ifaces
from z3c.form.browser.select import SelectWidget as z3cform_SelectWidget
from z3c.form.browser.text import TextWidget as z3cform_TextWidget
from z3c.form.interfaces import IEditForm
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import IForm
from z3c.form.interfaces import NO_VALUE
from z3c.form.widget import FieldWidget
from zope.component import getUtility
from zope.component import queryUtility
from zope.i18n import translate
from zope.interface import implementer
from zope.interface import implementer_only
from zope.schema import interfaces as schema_ifaces
from zope.schema.interfaces import IChoice
from zope.schema.interfaces import ICollection
from zope.schema.interfaces import ISequence
from zope.schema.interfaces import IVocabularyFactory

import collections


@implementer_only(ISelectWidget)
class SelectWidget(BaseWidget, z3cform_SelectWidget):
    """Select widget for z3c.form."""

    _base = SelectWidget

    pattern = "select2"
    pattern_options = BaseWidget.pattern_options.copy()

    separator = ";"
    noValueToken = ""
    noValueMessage = ""
    multiple = None
    orderable = False
    required = True

    @property
    def items(self):
        """
        Optionally handle ITreeVocabulary vocabs as dicts.
        """
        terms = self.terms
        if form_ifaces.ITerms.providedBy(terms):
            terms = terms.terms

        if schema_ifaces.ITreeVocabulary.providedBy(terms):
            groups = collections.OrderedDict()
            for group_term, option_terms in terms.items():
                group_widget = type(self)(self.request)
                group_widget.terms = option_terms
                group_label = group_term.title or group_term.value or group_term.token
                groups[group_label] = super(SelectWidget, group_widget).items
            return groups
        else:
            return super().items

    def _base_args(self):
        """Method which will calculate _base class arguments.

        Returns (as python dictionary):
            - `pattern`: pattern name
            - `pattern_options`: pattern options
            - `name`: field name
            - `value`: field value
            - `multiple`: field multiple
            - `items`: field items from which we can select to

        :returns: Arguments which will be passed to _base
        :rtype: dict
        """
        args = super()._base_args()
        args["name"] = self.name
        args["value"] = self.value
        args["multiple"] = self.multiple

        self.required = self.field.required

        options = args.setdefault("pattern_options", {})
        if self.multiple or ICollection.providedBy(self.field):
            args["multiple"] = self.multiple = True

        # ISequence represents an orderable collection
        if ISequence.providedBy(self.field) or self.orderable:
            options["orderable"] = True

        if self.multiple:
            options["separator"] = self.separator

        # Allow to clear field value if it is not required
        if not self.required:
            options["allowClear"] = True

        base_items = self.items
        if callable(base_items):
            # items used to be a property in all widgets, then in the select
            # widget it became a method, then in a few others too, but never in
            # all, so this was reverted to let it be a property again.  Let's
            # support both here to avoid breaking on some z3c.form versions.
            # See https://github.com/zopefoundation/z3c.form/issues/44
            base_items = base_items()

        def makeItem(item):
            """
            Gather the information needed by the widget for the given term.
            """
            if not isinstance(item["content"], str):
                item["content"] = translate(
                    item["content"], context=self.request, default=item["value"]
                )
            return (item["value"], item["content"])

        if isinstance(base_items, dict):
            items = collections.OrderedDict(
                (group_label, [makeItem(base_item) for base_item in group_options])
                for group_label, group_options in base_items.items()
            )
        else:
            items = [makeItem(item) for item in base_items]
        args["items"] = items

        return args

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


@implementer_only(IAjaxSelectWidget)
class AjaxSelectWidget(BaseWidget, z3cform_TextWidget):
    """Ajax select widget for z3c.form."""

    _base = InputWidget

    pattern = "select2"
    pattern_options = BaseWidget.pattern_options.copy()

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

    def _base_args(self):
        """Method which will calculate _base class arguments.

        Returns (as python dictionary):
            - `pattern`: pattern name
            - `pattern_options`: pattern options
            - `name`: field name
            - `value`: field value

        :returns: Arguments which will be passed to _base
        :rtype: dict
        """
        args = super()._base_args()
        args["name"] = self.name
        args["value"] = self.value
        args.setdefault("pattern_options", {})
        context = self.context
        field = None

        if IChoice.providedBy(self.field):
            args["pattern_options"]["maximumSelectionSize"] = 1
            field = self.field
        elif ICollection.providedBy(self.field):
            field = self.field.value_type
        if IChoice.providedBy(field):
            args["pattern_options"]["allowNewItems"] = "false"

        args["pattern_options"] = dict_merge(
            self._ajaxselect_options(), args["pattern_options"]
        )

        if field and getattr(field, "vocabulary", None):
            form_url = self.request.getURL()
            source_url = "{:s}/++widget++{:s}/@@getSource".format(
                form_url,
                self.name,
            )
            args["pattern_options"]["vocabularyUrl"] = source_url

        # ISequence represents an orderable collection
        if ISequence.providedBy(self.field) or self.orderable:
            args["pattern_options"]["orderable"] = True

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
            args["pattern_options"]["allowNewItems"] = str(
                allowNewItems,
            ).lower()

        return args


@implementer(IFieldWidget)
def SelectFieldWidget(field, request):
    return FieldWidget(field, SelectWidget(request))


@implementer(IFieldWidget)
def AjaxSelectFieldWidget(field, request, extra=None):
    if extra is not None:
        request = extra
    return FieldWidget(field, AjaxSelectWidget(request))
