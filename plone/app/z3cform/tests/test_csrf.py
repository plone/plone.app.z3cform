from plone.protect.tests.case import KeyringTestCase


class TestAuthenticatedButtonActions(KeyringTestCase):
    def test_execute(self):
        from Acquisition import Implicit
        from plone.app.z3cform.csrf import AuthenticatedButtonActions
        from plone.protect import createToken
        from Testing.makerequest import makerequest

        class DummyForm:
            enableCSRFProtection = True

        class DummyAction:
            def isExecuted(self):
                return True

            def execute(self):
                self.called = True

        form = DummyForm()
        request = makerequest(Implicit()).REQUEST
        request.form["_authenticator"] = createToken()
        actions = AuthenticatedButtonActions(form, request, None)
        actions["foo"] = DummyAction()

        actions.execute()
        # If we got here without raising Unauthorized, the test passed.
