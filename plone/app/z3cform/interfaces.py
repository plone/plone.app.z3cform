from zope.interface import Interface
from z3c.form.interfaces import IFormLayer


class IPloneFormLayer(IFormLayer):
    """Request layer installed via browserlayer.xml
    """


class IAriaHelperView(Interface):
    """Helper view to get ARIA attributes
    """

    def describedby():
        """Identifies the element that describes the field input.
        """

    def required():
        """Indicates that user input is required on the element before a form may be submitted.
        """
