=====================
KSS inline validation
=====================

First, let's set up KSS debug mode:

    >>> from zope.interface import alsoProvides
    >>> from Testing.ZopeTestCase import ZopeLite
    >>> from Testing.makerequest import makerequest
    >>> from kss.core.tests.base import IDebugRequest
    >>> from zope.annotation.interfaces import IAttributeAnnotatable

    >>> app = ZopeLite.app()
    >>> def make_request(form={}, lang='en'):
    ...     request = makerequest(app, environ = {'HTTP_ACCEPT_LANGUAGE': lang}).REQUEST
    ...     request.form.update(form)
    ...     alsoProvides(request, IDebugRequest)
    ...     alsoProvides(request, IAttributeAnnotatable)
    ...     return request

Then we create a simple z3c form

    >>> from zope import interface, schema
    >>> from z3c.form import form, field, button
    >>> from plone.app.z3cform.layout import FormWrapper

    >>> class MySchema(interface.Interface):
    ...     age = schema.Int(title=u"Age")

    >>> class MyForm(form.Form):
    ...     fields = field.Fields(MySchema)
    ...     ignoreContext = True # don't use context to get widget data
    ...
    ...     @button.buttonAndHandler(u'Apply')
    ...     def handleApply(self, action):
    ...         data, errors = self.extractData()
    ...         print data['age'] # ... or do stuff

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
    >>> from zope.interface import Interface, implements
    >>> from Acquisition import Implicit
    >>> class Bar(Implicit):
    ...     implements(Interface)
    ...     def restrictedTraverse(self, name):
    ...         # fake traversal to the form
    ...         if name.startswith('@@'):
    ...             return getMultiAdapter((self, self._REQUEST), Interface, name[2:]).__of__(self)
    ...         else:
    ...             return getattr(self, name)
    ...         
    >>> context = Bar()
    >>> request = make_request()
    >>> context._REQUEST = request # evil test fake
    >>> formWrapper = getMultiAdapter((context, request), name=u"test-form")
    >>> formWrapper
    <Products.Five.metaclass.MyFormWrapper object ...>
    >>> formWrapper.form
    <class 'plone.app.z3cform.tests.example.MyForm'>

    >>> del context, request

Inline validation
=================

Inline validation is invoked via the @@kss_z3cform_inline_validation view.

    >>> context = Bar()
    >>> request = make_request(form={'form.widgets.age': 'Title'})
    >>> context._REQUEST = request
    >>> view = getMultiAdapter((context, request), name=u"kss_z3cform_inline_validation")

This is wired up with KSS. When the user leaves a form control with inline
validation enabled, it will be called with the following parameters:

    >>> view.validate_input(formname=u'test-form', fieldname=u'form.widgets.age', value='Title')
    [{'selectorType': 'css', 'params': {'html': u'<![CDATA[The entered value is not a valid integer literal.]]>', 'withKssSetup': u'True'},
      'name': 'replaceInnerHTML',
      'selector': u'#formfield-form-widgets-age div.fieldErrorBox'},
     {'selectorType': 'css',
      'params': {'value': u'error'},
      'name': 'addClass',
      'selector': u'#formfield-form-widgets-age'}]

    >>> request = make_request(form={'form.widgets.age': '20'})
    >>> context._REQUEST = request
    >>> view = getMultiAdapter((context, request), name=u"kss_z3cform_inline_validation")
    >>> view.validate_input(formname=u'test-form', fieldname=u'form.widgets.age', value='20')
    [{'selectorType': 'css', 'params': {}, 'name': 'clearChildNodes', 'selector': u'#formfield-form-widgets-age div.fieldErrorBox'},
     {'selectorType': 'css', 'params': {'value': u'error'}, 'name': 'removeClass', 'selector': u'#formfield-form-widgets-age'},
     {'selectorType': 'css', 'params': {'name': u'display', 'value': u'none'}, 'name': 'setStyle', 'selector': '.portalMessage'},
     {'selectorType': 'htmlid', 'params': {'html': u'<![CDATA[<dt>Info</dt><dd></dd>]]>', 'withKssSetup': u'True'},
      'name': 'replaceInnerHTML', 'selector': 'kssPortalMessage'},
     {'selectorType': 'htmlid', 'params': {'name': u'class', 'value': u'portalMessage info'},
      'name': 'setAttribute', 'selector': 'kssPortalMessage'},
     {'selectorType': 'htmlid', 'params': {'name': u'display', 'value': u'none'}, 'name': 'setStyle', 'selector': 'kssPortalMessage'}]

Inline validation with groups
=============================

We use plone.app.z3cform.tests.example.MyGroupFormWrapper and validate the 
field 'name' that's part of a group. Inline validation is invoked via the 
@@kss_z3cform_inline_validation view.

    >>> request = make_request(form={'form.widgets.name': ''})
    >>> context._REQUEST = request
    >>> view = getMultiAdapter((context, request), name=u"kss_z3cform_inline_validation")

The validation view takes an Attribute fieldset with the index of the group.

    >>> view.validate_input(formname=u'test-group-form', fieldname=u'form.widgets.name', fieldset="0", value='')
    [{'selectorType': 'css', 'params': {'html': u'<![CDATA[Required input is missing.]]>', 'withKssSetup': u'True'},
      'name': 'replaceInnerHTML',
      'selector': u'#fieldset-0 #formfield-form-widgets-name div.fieldErrorBox'},
     {'selectorType': 'css',
      'params': {'value': u'error'},
      'name': 'addClass',
      'selector': u'#fieldset-0 #formfield-form-widgets-name'}]

    >>> request = make_request(form={'form.widgets.name': u'Name'})
    >>> context._REQUEST = request
    >>> view = getMultiAdapter((context, request), name=u"kss_z3cform_inline_validation")
    >>> view.validate_input(formname=u'test-group-form', fieldname=u'form.widgets.name', fieldset="0", value=u'Name')
    [{'selectorType': 'css', 'params': {}, 'name': 'clearChildNodes', 'selector': u'#fieldset-0 #formfield-form-widgets-name div.fieldErrorBox'},
     {'selectorType': 'css', 'params': {'value': u'error'}, 'name': 'removeClass', 'selector': u'#fieldset-0 #formfield-form-widgets-name'},
     {'selectorType': 'css', 'params': {'name': u'display', 'value': u'none'}, 'name': 'setStyle', 'selector': '.portalMessage'},
     {'selectorType': 'htmlid', 'params': {'html': u'<![CDATA[<dt>Info</dt><dd></dd>]]>', 'withKssSetup': u'True'},
      'name': 'replaceInnerHTML', 'selector': 'kssPortalMessage'},
     {'selectorType': 'htmlid', 'params': {'name': u'class', 'value': u'portalMessage info'},
      'name': 'setAttribute', 'selector': 'kssPortalMessage'},
     {'selectorType': 'htmlid', 'params': {'name': u'display', 'value': u'none'}, 'name': 'setStyle', 'selector': 'kssPortalMessage'}]


Inline-Validation and Translation of ErrorSnippets
==================================================

We use plone.app.z3cform.tests.example.MyGroupFormWrapper and validate the 
field 'name' that's part of a group. Inline validation is invoked via the 
@@kss_z3cform_inline_validation view.

    >>> request = make_request(form={'form.widgets.name': ''}, lang='de',)
    >>> context._REQUEST = request
    >>> view = getMultiAdapter((context, request), name=u"kss_z3cform_inline_validation")

The validation view takes an Attribute fieldset with the index of the group.

    >>> view.validate_input(formname=u'test-group-form', fieldname=u'form.widgets.name', fieldset="0", value='')
    [{'selectorType': 'css', 'params': {'html': u'<![CDATA[Erforderliche Eingabe fehlt.]]>', 'withKssSetup': u'True'},
      'name': 'replaceInnerHTML',
      'selector': u'#fieldset-0 #formfield-form-widgets-name div.fieldErrorBox'},
     {'selectorType': 'css',
      'params': {'value': u'error'},
      'name': 'addClass',
      'selector': u'#fieldset-0 #formfield-form-widgets-name'}]
