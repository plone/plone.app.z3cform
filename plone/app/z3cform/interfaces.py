from plone.app.textfield.widget import IRichTextWidget as patextfield_IRichTextWidget
from plone.schema.interfaces import IFormLayer
from z3c.form.interfaces import ICheckBoxWidget as ICheckBoxWidgetBase
from z3c.form.interfaces import IOrderedSelectWidget as IOrderedSelectWidgetBase
from z3c.form.interfaces import IRadioWidget as IRadioWidgetBase
from z3c.form.interfaces import ISelectWidget as ISelectWidgetBase
from z3c.form.interfaces import ISingleCheckBoxWidget
from z3c.form.interfaces import ISubmitWidget as ISubmitWidgetBase
from z3c.form.interfaces import ITextAreaWidget as ITextAreaWidgetBase
from z3c.form.interfaces import ITextLinesWidget as ITextLinesWidgetBase
from z3c.form.interfaces import ITextWidget as ITextWidgetBase
from zope.deferredimport import deprecated
from zope.interface import Interface


# this should not be used anymore

deprecated(
    "Use zope.schema.interfaces.IDate instead (will be removed in Plone 7).",
    IDateField="zope.schema.interfaces:IDate",
)

deprecated(
    "Use zope.schema.interfaces.IDatetime instead (will be removed in Plone 7).",
    IDatetimeField="zope.schema.interfaces:IDatetime",
)


class IPloneFormLayer(IFormLayer):
    """Request layer installed via browserlayer.xml"""


class IFieldPermissionChecker(Interface):
    """Adapter factory for checking whether a user has permission to
    edit a specific field on a content object.
    """

    def validate(field_name, vocabulary_name=None):
        """Returns True if the current user has permission to edit the
        `field_name` field.  Returns False if the user does not have
        permission.  Raises and AttributeError if the field cannot be
        found.
        """


class ITextWidget(ITextWidgetBase):
    """Marker interface for base text input"""


class ITextAreaWidget(ITextAreaWidgetBase):
    """Marker interface for base text input"""


class ITextLinesWidget(ITextLinesWidgetBase):
    """Marker interface for base text input"""


class IDateWidget(ITextWidget):
    """Marker interface for the DateWidget."""


class IDatetimeWidget(ITextWidget):
    """Marker interface for the DatetimeWidget."""


class ITimeWidget(ITextWidget):
    """Marker interface for the TimeWidget"""


class IOrderedSelectWidget(IOrderedSelectWidgetBase):
    """Marker interface for the OrderedSelectWidget."""


class ISelectWidget(ISelectWidgetBase):
    """Marker interface for the SelectWidget."""


class ISelect2Widget(ISelectWidget):
    """Marker interface for the Select2Widget."""


class IAjaxSelectWidget(ITextWidget):
    """Marker interface for the AjaxSelectWidget."""


class IQueryStringWidget(ITextWidget):
    """Marker interface for the QueryStringWidget."""


class IRelatedItemsWidget(ITextWidget):
    """Marker interface for the RelatedItemsWidget."""


class IContentBrowserWidget(ITextWidget):
    """Marker interface for the RelatedItemsWidget."""


class IRichTextWidget(patextfield_IRichTextWidget):
    """Marker interface for the TinyMCEWidget."""


class ILinkWidget(ITextWidget):
    """Marker interface for the enhanced link widget."""


class IEmailWidget(ITextWidget):
    """Marker interface for the dumb email widget."""


class IPasswordWidget(ITextWidget):
    """Marker interface for the password widget."""


class ISubmitWidget(ISubmitWidgetBase):
    """Marker interface for SubmitWidget."""


class ICheckBoxWidget(ICheckBoxWidgetBase):
    """Marker for CheckBoxWidget."""


class ISingleCheckBoxBoolWidget(ISingleCheckBoxWidget):
    """Marker interface for the SingleCheckboxBoolWidget."""


class IRadioWidget(IRadioWidgetBase):
    """Radio widget."""

    def renderForValue(value):
        """Render a single radio button element for a given value.

        Here the word ``value`` is used in the HTML sense, in other
        words it is a term token.
        """


class IRichTextWidgetInputModeRenderer(Interface):
    """Marker interface to render multiple wysiwyg editors"""
