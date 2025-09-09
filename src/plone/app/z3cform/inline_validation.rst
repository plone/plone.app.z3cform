Inline validation
=================

First, let's set up some infrastructure:

    >>> from zope.interface import alsoProvides
    >>> from plone.testing.zope import makeTestRequest
    >>> from zope.annotation.interfaces import IAttributeAnnotatable
    >>> from z3c.form.interfaces import IFormLayer

    >>> app = layer['app']
    >>> def make_request(form=None, lang='en'):
    ...     request = makeTestRequest({'HTTP_ACCEPT_LANGUAGE': lang})
    ...     if form is None:
    ...         form = {}
    ...     request.form.update(form)
    ...     alsoProvides(request, IFormLayer)
    ...     alsoProvides(request, IAttributeAnnotatable)
    ...     return request

Then we create a simple z3c form

    >>> from zope import interface, schema
    >>> from z3c.form import form, field, button
    >>> from plone.z3cform.layout import FormWrapper

    >>> class MySchema(interface.Interface):
    ...     age = schema.Int(title=u"Age")

    >>> from __future__ import print_function
    >>> class MyForm(form.Form):
    ...     fields = field.Fields(MySchema)
    ...     ignoreContext = True # don't use context to get widget data
    ...
    ...     @button.buttonAndHandler(u'Apply')
    ...     def handleApply(self, action):
    ...         data, errors = self.extractData()
    ...         print(data['age'])  # ... or do stuff

    >>> class MyFormWrapper(FormWrapper):
    ...     form = MyForm
    ...     label = u"Please enter your age"

    >>> from zope.component import provideAdapter
    >>> from zope.publisher.interfaces.browser import IBrowserRequest
    >>> from zope.interface import Interface

    >>> provideAdapter(adapts=(Interface, IBrowserRequest),
    ...                provides=Interface,
    ...                factory=MyFormWrapper,
    ...                name=u"test-form")

Let's verify that worked:

    >>> from zope.component import getMultiAdapter
    >>> from zope.interface import Interface, implementer
    >>> from Acquisition import Implicit
    >>> @implementer(Interface)
    ... class Bar(Implicit):
    ...     def restrictedTraverse(self, name):
    ...         # fake traversal to the form
    ...         if name.startswith('@@'):
    ...             return getMultiAdapter((self, self._REQUEST), Interface, name[2:])
    ...         else:
    ...             return getattr(self, name)
    ...
    >>> context = Bar()
    >>> request = make_request()
    >>> context._REQUEST = request # evil test fake
    >>> formWrapper = getMultiAdapter((context, request), name=u"test-form")
    >>> formWrapper
    <Products.Five...MyFormWrapper object ...>
    >>> formWrapper.form
    <class 'plone.app.z3cform.tests.example.MyForm'>

    >>> del context, request

Inline validation
-----------------

Inline validation is invoked via the @@z3cform_validate_field view.

    >>> context = Bar()
    >>> request = make_request(form={'form.widgets.age': 'Title'})
    >>> context._REQUEST = request
    >>> form = MyForm(context, request)
    >>> z3cform_validate_field = getMultiAdapter((form, request), name=u"z3cform_validate_field")

This is wired up with jQuery. When the user leaves a form control with inline
validation enabled, it will be called with the following parameters:

    >>> z3cform_validate_field(fname=u'form.widgets.age')
    '{"errmsg": "The entered value is not a valid integer literal."}'

    >>> request = make_request(form={'form.widgets.age': '20'})
    >>> context._REQUEST = request
    >>> form = MyForm(context, request)
    >>> z3cform_validate_field = getMultiAdapter((form, request), name=u"z3cform_validate_field")
    >>> z3cform_validate_field(fname=u'form.widgets.age')
    '{"errmsg": ""}'

If the field name (fname) is not provided by the client, the validation
should return without issue:

    >>> z3cform_validate_field()
    '{"errmsg": ""}'
    >>> z3cform_validate_field(fname=None)
    '{"errmsg": ""}'

Inline validation with groups
-----------------------------

We use plone.app.z3cform.tests.example.MyGroupFormWrapper and validate the
field 'name' that's part of a group. Inline validation is invoked via the
@@z3cform_validate_field view.

    >>> request = make_request(form={'form.widgets.name': ''})
    >>> context._REQUEST = request
    >>> from plone.app.z3cform.tests.example import MyGroupFormWrapper
    >>> form = MyGroupFormWrapper(context, request)
    >>> z3cform_validate_field = getMultiAdapter((form, request), name=u"z3cform_validate_field")

The validation view takes an Attribute fset with ether the numeric index or
the name of the group.

    >>> z3cform_validate_field(fname=u'form.widgets.name', fset="0")
    '{"errmsg": "Required input is missing."}'
    >>> z3cform_validate_field(fname=u'form.widgets.name', fset="mygroup")
    '{"errmsg": "Required input is missing."}'

    >>> request = make_request(form={'form.widgets.name': u'Name'})
    >>> context._REQUEST = request
    >>> form = MyGroupFormWrapper(context, request)
    >>> z3cform_validate_field = getMultiAdapter((form, request), name=u"z3cform_validate_field")
    >>> z3cform_validate_field(fname=u'form.widgets.name', fset="0")
    '{"errmsg": ""}'
    >>> z3cform_validate_field(fname=u'form.widgets.name', fset="mygroup")
    '{"errmsg": ""}'


Inline-Validation and Translation of ErrorSnippets
--------------------------------------------------

We use plone.app.z3cform.tests.example.MyGroupFormWrapper and validate the
field 'name' that's part of a group. Inline validation is invoked via the
@@z3cform_validate_field view.

    >>> request = make_request(form={'form.widgets.name': ''}, lang='de',)
    >>> context._REQUEST = request
    >>> form = MyGroupFormWrapper(context, request)
    >>> z3cform_validate_field = getMultiAdapter((form, request), name=u"z3cform_validate_field")

The validation view takes an Attribute fieldset with the index of the group.
The error is only shown when warning_only is explicitly switched off (matching
the behavior of archetypes.)

    >>> z3cform_validate_field(fname=u'form.widgets.name', fset="0")
    '{"errmsg": "Erforderliche Eingabe fehlt."}'


Forms embedded inside normal views
-----------------------------------

It's possible to embed z3c.form Forms inside a normal BrowserView via viewlets,
portlets or tiles.

Currently the name of the form to be validated is gotten from the URL. For embedded
forms this can't work since the URL only has the containing view's name.

Until a lasting solution is found, we just make sure that validation
doesn't raise an exception if it receives a normal browerview as the supposed
form.

    >>> from zope.publisher.browser import BrowserView
    >>> class MyNormalView(BrowserView):
    ...     """ """

    >>> provideAdapter(adapts=(Interface, IBrowserRequest),
    ...                provides=Interface,
    ...                factory=MyNormalView,
    ...                name=u"my-view")

Let's verify that it gets called...

    >>> context = Bar()
    >>> request = make_request()
    >>> view = getMultiAdapter((context, request), name=u"my-view")
    >>> view
    <MyNormalView object ...>

Inline validation is invoked via the @@z3cform_validate_field view. But
in this case no validation output should be returned.

    >>> context = Bar()
    >>> request = make_request(form={'form.widgets.age': 'Title'})
    >>> z3cform_validate_field = getMultiAdapter((view, request), name=u"z3cform_validate_field")
    >>> z3cform_validate_field(fname=u'form.widgets.age')
    '{"errmsg": ""}'
