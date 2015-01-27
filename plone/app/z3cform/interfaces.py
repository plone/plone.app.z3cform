from z3c.form.interfaces import IFormLayer
from zope.schema.interfaces import IDate
from zope.schema.interfaces import IDatetime
from z3c.form.interfaces import ISelectWidget as IBaseSelectWidget
from z3c.form.interfaces import ITextWidget
from plone.app.textfield.widget import IRichTextWidget as patextfield_IRichTextWidget


class IPloneFormLayer(IFormLayer):
    """Request layer installed via browserlayer.xml
    """


class IDateField(IDate):
    """Marker interface for the DateField."""


class IDatetimeField(IDatetime):
    """Marker interface for the DatetimeField."""


class IDateWidget(ITextWidget):
    """Marker interface for the DateWidget."""


class IDatetimeWidget(ITextWidget):
    """Marker interface for the DatetimeWidget."""


class ISelectWidget(IBaseSelectWidget):
    """Marker interface for the SelectWidget."""


class IAjaxSelectWidget(ITextWidget):
    """Marker interface for the Select2Widget."""


class IQueryStringWidget(ITextWidget):
    """Marker interface for the QueryStringWidget."""


class IRelatedItemsWidget(ITextWidget):
    """Marker interface for the RelatedItemsWidget."""


class IRichTextWidget(patextfield_IRichTextWidget):
    """Marker interface for the TinyMCEWidget."""
