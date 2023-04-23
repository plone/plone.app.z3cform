from Acquisition import aq_base
from plone.app.z3cform.utils import call_callables
from z3c.form.widget import Widget


class PatternNotImplemented(Exception):
    """Raised when method/property is not implemented"""


class BaseWidget(Widget):
    """Base widget for z3c.form."""

    pattern = None
    pattern_options = {}
    _adapterValueAttributes = Widget._adapterValueAttributes + ("pattern_options",)

    def _base(self, pattern, pattern_options={}):
        """Base widget class."""
        raise PatternNotImplemented

    def _base_args(self):
        """Method which will calculate _base class arguments.

        Returns (as python dictionary):
            - `pattern`: pattern name
            - `pattern_options`: pattern options

        :returns: Arguments which will be passed to _base
        :rtype: dict
        """
        if self.pattern is None:
            raise PatternNotImplemented("'pattern' option is not provided.")
        return {
            "pattern": self.pattern,
            "pattern_options": self.pattern_options.copy(),
        }

    def render(self):
        """Render widget.

        :returns: Widget's HTML.
        :rtype: string
        """
        if self.mode != "input":
            return super().render()

        _base_args = self._base_args()
        _base_args["pattern_options"] = call_callables(
            _base_args["pattern_options"],
            self.context,
        )

        pattern_widget = self._base(**_base_args)
        if getattr(self, "klass", False):
            pattern_widget.klass = "{} {}".format(
                pattern_widget.klass,
                self.klass,
            )
        return pattern_widget.render()

    def is_subform_widget(self):
        return getattr(aq_base(self.form), "parentForm", None) is not None
