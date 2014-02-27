=================
plone.app.z3cform
=================

A Plone specific integration and HTML mark-up for z3c.form.

.. contents:: Table of Contents

Introduction
==============

This Plone package is aimed for developers who want to create forms
in Python code.

Please read the documentation for `z3c.form`_, which contains important
information about using z3c.form in Zope 2 in general. For the most part,
that package contains the "active" parts that you need to know about, and
this package provides "passive" overrides that make the forms integrate with
Plone.

Installation
============

Plone 4.1 and later include *plone.app.z3cform* in Plone core. Older versions need to install
the addon separately as your own add-on dependency.

Features
============

The following Plone and z3c.form integration is added

* Plone *main_template.pt* integration

* Plone specific widget frame

* Date/time pickers

* WYSIWYG widget (TinyMCE visual editor with Plone support)

* CRUD forms

Out of the box form templates
==================================

The form and widget templates are applied in the following order

* *plone.app.z3cform* specific

* *plone.z3cform* specific

* *z3c.form* specific

*plone.app.z3cform* package overrides the ``@@ploneform-macros`` view from `plone.z3cform`_,
using standard Plone markup for form fields, fieldsets, etc.

All the macros described in `plone.z3cform`_ are still available. In addition,
you can use the ``widget_rendering`` macro to render all the default widgets,
but none of the fieldsets (groups) or the fieldset headers (which would be
rendered with the ``fields`` macro).

Each widget is rendered using the ``@@ploneform-render-widget`` view, which by
default includes the widget's label, required indicator, description, errors,
and the result of ``widget.render()``.  This view may be overridden for
particular widget types in order to customize this widget chrome.

Customizing form behavior
============================

Form method
-------------

If your form instance defines a property called ``method`` it allows
you to set whether form is HTTP POST or HTTP GET. The default is POST.
This translates to ``<form method="post">`` attribute.

Example::

    class HolidayServiceSearchForm(form.Form):
            """ Example search form of which results can be bookmarked.

            Bookmarking is possible because we use HTTP GET method.
            """

            method = "get"

Form action
------------

Form ``action`` property defines HTTP target where the form is posted. The default is
the same page where the form was rendered, ``request.getURL()``.

Example::

        class HolidayServiceSearchForm(form.Form):

            def action(self):
                """ Redefine <form action=''> attribute.

                We use URL fragment to define the <a> anchor
                were we directly scroll at the results when the form is posted,
                skipping unnecessary form fields part. The user can scroll
                back there if he/she wants modify the parameters.
                """

                # Context item URL + form view name + link fragment.
                # This works for HTTP GET forms only.
                # Note that we cannot use request.getURL() as it might contain
                # 1) prior fragment 2) GET query parameters messing up the UrL
                return self.context.absolute_url() + "/holidayservice_view" + "#searched"

Fieldsets and tabs
--------------------

You can fieldsets to your form if you subclass the form from z3c.form.group.GroupForm.
The default behavior of Plone is to turn these fieldsets to tabs (as seen on
any *Edit* view of content item).

You can disable this behavior for your form::



    class ReportForm(z3c.form.group.GroupForm, z3c.form.form.Form):

        # Disable turn fieldsets to tabs behavior
        enable_form_tabbing  = False

Unload protection
-----------------

The default behaviour on Plone is to add a confirm box
if you leave a form you have modified without having submitted it.

You can disable this behavior for your form::

    class SearchForm(z3c.form.group.GroupForm, z3c.form.form.Form):

        # Disable unload protection behavior
        enable_unload_protection  = False


CSRF Protection
===============

A common vulnerability affecting web forms is cross-site request forgery (CSRF).
This attack occurs when the user of your site visits a third-party site that
uses Javascript to post to a URL on your site without the user's knowledge,
taking advantage of the user's active session.



plone.app.z3cform can protect against this type of attack by adding a unique
token as a hidden input when rendering the form, and checking to make sure it
is present as a request parameter when form actions are executed.

To turn on this protection, enable the form's enableCSRFProtection attribute.
Example::

    class PasswordForm(form.Form):
        """Form to set the user's password."""
        enableCSRFProtection = True

Form main template override
=============================

Forms are framed by *FormWrapper* views. It places rendered
form inside Plone page frame. The default *FormWrapper* is supplied automatically,
but you can override it.

Below is a placeholder example with few `<select>` inputs.

Example ``reporter.py``::

    import zope.schema
    import zope.interface
    from zope.i18nmessageid import MessageFactory
    from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile as FiveViewPageTemplateFile

    from zope.schema.vocabulary import SimpleVocabulary
    from zope.schema.vocabulary import SimpleTerm

    import z3c.form

    import plone.app.z3cform
    import plone.z3cform.templates

    _ = MessageFactory('your.addon')


    def make_terms(items):
        """ Create zope.schema terms for vocab from tuples """
        terms = [SimpleTerm(value=pair[0], token=pair[0], title=pair[1]) for pair in items]
        return terms


    output_type_vocab = SimpleVocabulary(make_terms([("list", "Patient list"), ("summary", "Summary")]))


    class IReportSchema(zope.interface.Interface):
        """ Define reporter form fields """
        outputType = zope.schema.Choice(
            title=u"Output type",
            description=u"How do you want the output",
            source=output_type_vocab)

        country = zope.schema.Choice(
            title=u"Country",
            required=False,
            description=u"Which country to report",
            vocabulary="allowed_countries")

        hospital = zope.schema.Choice(
            title=u"Hospital",
            required=False,
            description=u"Which hospital to report",
            vocabulary="allowed_hospitals")


    class ReportForm(z3c.form.form.Form):
        """ A form to output a HTML report from chosen parameters """

        fields = z3c.form.field.Fields(IReportSchema)

        ignoreContext = True

        output = None

        @z3c.form.button.buttonAndHandler(_('Make Report'), name='report')
        def report(self, action):
            data, errors = self.extractData()
            if errors:
                self.status = "Please correct errors"
                return

            # Create sample item which we can consume in the page template
            self.output = dict(country="foobar")

            self.status = _(u"Report complete")


    # IF you want to customize form frame you need to make a custom FormWrapper view around it
    # (default plone.z3cform.layout.FormWrapper is supplied automatically with form.py templates)
    report_form_frame = plone.z3cform.layout.wrap_form(ReportForm, index=FiveViewPageTemplateFile("templates/reporter.pt"))

Example ``configure.zcml``::

    <configure
        xmlns="http://namespaces.zope.org/zope"
        xmlns:browser="http://namespaces.zope.org/browser"
        i18n_domain="your.addon">

       <browser:page
           for="*"
           name="reporter"
           class=".reporter.report_form_frame"
           permission="zope2.View"
           />

    </configure>


Example ``templates/reporter.html``::

    <html metal:use-macro="context/main_template/macros/master"
          i18n:domain="sits.reporttool">
    <body>

        <metal:block fill-slot="main">

            <h1 class="documentFirstHeading" tal:content="view/label | nothing" />

            <div id="content-core">

                <div id="form-input">
                    <span tal:replace="structure view/contents" />
                </div>

                <div id="form-output" tal:condition="view/form_instance/output">
                    Chosen country: <b tal:content="view/form_instance/output/country" />
                </div>
            </div>

        </metal:block>

    </body>
    </html>

Widget frame override
=============================

You can override widget templates as instructed for ``z3c.form``.
``plone.app.z3cform`` renders `a frame around each widget <https://github.com/plone/plone.app.z3cform/blob/master/plone/app/z3cform/templates/widget.pt>`_
which usually consists of

* Label

* Required marker

* Description

You might want to customize this widget frame for your own form.
Below is an example how to do it.

* Copy `widget.pt <https://github.com/plone/plone.app.z3cform/blob/master/plone/app/z3cform/templates/widget.pt>`_ to your own package and customize it in way you wish

* Add the following to ``configure.zcml``

::

    <browser:page
        name="ploneform-render-widget"
        for=".demo.IDemoWidget"
        class="plone.app.z3cform.templates.RenderWidget"
        permission="zope.Public"
        template="demo-widget.pt"
        />

* Create a new marker interface in Python code

::

    from zope.interface import Interface

    class IDemoWidget(Interface):
        pass

* Then apply this marker interface to all of your widgets in ``form.update()``

::

    from zope.interface import alsoProvides

    class MyForm(...):
        ...
        def update(self):
            super(MyForm, self).update()
            for widget in form.widgets.values():
                alsoProvides(widget, IDemoWidget)

Hide fields that have no value
==================================

The ``.empty`` css class marks the fields that have no value. If you don't want
to display these fields in view mode, add the following css in your theme::

    .template-view .empty.field {
       display: none;
    }

Testing
===============

To test ``plone.app.z3form`` it is recommended to use
`plone.app.testing <https://pypi.python.org/pypi/plone.app.testing/>`_
function test layer which will do ``plone.app.z3cform`` setup for you.
Read ``plone.app.z3cform`` manual for further instructions.

If you still need to test forms on lower level in unit tests
you need to enable ``plone.app.z3cform`` support manually.
Below is an example::

    import unittest2 as unittest

    from zope.interface import alsoProvides
    from zope.publisher.browser import setDefaultSkin

    from z3c.form.interfaces import IFormLayer

    class TestFilteringIntegration(unittest.TestCase):
        """ Test that filtering options work on the form """

        layer = MY_TEST_LAYER_WITH_PLONE

        def setUp(self):
            super(TestFilteringIntegration, self).setUp()
            request = self.layer["request"]
            setDefaultSkin(request)
            alsoProvides(request, IFormLayer) #suitable for testing z3c.form views

        def test_report_form_filtering(self):
            reporter = ReportForm(self.layer["portal"], self.layer["request"])
            reporter.update()



Troubleshooting
================

Here are some common errors you might encounter with plone.app.z3cform.

ComponentLookupError in updateWidgets()
----------------------------------------

::

        Traceback (innermost last):
          Module ZPublisher.Publish, line 119, in publish
          Module ZPublisher.mapply, line 88, in mapply
          Module ZPublisher.Publish, line 42, in call_object
          Module plone.z3cform.layout, line 64, in __call__
          Module plone.z3cform.layout, line 54, in update
          Module getpaid.expercash.browser.views, line 63, in update
          Module z3c.form.form, line 208, in update
          Module z3c.form.form, line 149, in update
          Module z3c.form.form, line 128, in updateWidgets
          Module zope.component._api, line 103, in getMultiAdapter
        ComponentLookupError: ((<getpaid.expercash.browser.views.CheckoutForm object at 0xdb052ac>, <HTTPRequest, URL=http://localhost:8080/test/@@getpaid-checkout-wizard>, <PloneSite at /test>), <InterfaceClass z3c.form.interfaces.IWidgets>, u'')

plone.app.z3cform layers are not in place (configuration ZCML is not read). You probably forgot to include plone.app.z3cform in your
product's configuration.zcml. See *Installation* above.


KSS inline validation (deprecated)
====================================

.. note ::

    Plone 4.3+ and later no longer includes KSS

This package installs AJAX handlers to perform inline field validation. On any
form, the field will be validated when the user blurs a field.

This relies on the KSS framework, and is only installed if ``plone.app.kss``
is available. If you are using a custom form, note that you must define the
following "kassattr" variables:

* ``formname``, the name of the form view, defined on the ``<form />``
  element.
* ``fieldname``, the name of the current field (same as the widget name),
  defined on an element wrapping the field.
* ``fieldset``, defined for non-default fieldsets on the ``<fieldset />``
  element.

This also assumes the standard Plone form markup is used. See
``templaes/macros.pt`` for details.

.. _z3c.form: http://pypi.python.org/pypi/z3c.form
.. _Plone: http://plone.org
.. _plone.z3cform: http://pypi.python.org/pypi/plone.z3cform
