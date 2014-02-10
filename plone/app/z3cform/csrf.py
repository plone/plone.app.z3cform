from plone.app.z3cform.interfaces import IPloneFormLayer
from plone.protect import CheckAuthenticator
from z3c.form.button import ButtonActions
from z3c.form.interfaces import IButtonForm
from zope.component import adapts
from zope.interface import Interface


class AuthenticatedButtonActions(ButtonActions):
    """z3c.form action manager that checks Plone's CSRF authenticator.

    The check is performed if the form's enableCSRFProtection attribute is
    True.
    """
    adapts(IButtonForm, IPloneFormLayer, Interface)

    def execute(self):
        if getattr(self.form, 'enableCSRFProtection', False):
            if self.executedActions:
                CheckAuthenticator(self.request)
        super(AuthenticatedButtonActions, self).execute()
