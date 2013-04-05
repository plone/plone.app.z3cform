=================
plone.app.z3cform
=================

A collection of widgets and templates, and other components for use
with `z3c.form`_ in Plone_.  This extends `plone.z3cform`_, the library that
enables Zope 2 applications to use z3c.form, with Plone-specific markup and
functionality.

Please read the documentation for `z3c.form`_, which contains important
information about using z3c.form in Zope 2 in general. For the most part,
that package contains the "active" parts that you need to know about, and
this package provides "passive" overrides that make the forms integrate with
Plone.

.. contents:: Table of Contents

Installation
============

To use z3c.form forms in Plone, you should install this package. First,
depend on it in your own package's ``setup.py``, using the
``install_requires`` list. Then load its configuration form your own package's
``configure.zcml``, with::

    <include package="plone.app.z3cform" />

Before you can use the forms, you also need to install the
``plone.app.z3cform:default`` GenericSetup extension profile. The best way
to do that is to install it as a dependency of your own product's installation
profile. In your ``metadata.xml``, add a dependency like::

    <metadata>
        ...
        <dependencies>
            ...
            <dependency>profile-plone.app.z3cform:default</dependency>
        </dependencies>
    </metadata>

Note that if you don't install the product, and you are using standalone
z3c.form forms (in Zope 2.12 or later), you will find that z3c.form complains
about missing widgets. This is because the ``IFormLayer`` marker interface
has not been applied to the request.

In fact, the browser layer installed with this product's extension profile is
``plone.app.z3cform.interfaces.IPloneFormLayer``, which in turn derives from
``z3c.form.interfaces.IFormLayer``.

Default macros
==============

This package overrides the ``@@ploneform-macros`` view from `plone.z3cform`_,
using standard Plone markup for form fields, fieldsets, etc.

All the macros described in `plone.z3cform`_ are still available. In addition,
you can use the ``widget_rendering`` macro to render all the default widgets,
but none of the fieldsets (groups) or the fieldset headers (which would be
rendered with the ``fields`` macro).

Each widget is rendered using the ``@@ploneform-render-widget`` view, which by
default includes the widget's label, required indicator, description, errors,
and the result of ``widget.render()``.  This view may be overridden for
particular widget types in order to customize this widget chrome.

Inline form validation
======================

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

Template enhancements
========================

The following apply in plone.app.z3cform templates which are defined in
``plone.app.z3cform/plone/app/z3cform/templates/macros.pt``.
They allow you to customize the behavior of z3c.form package to play
nicely with your application.

plone.app.z3cform add-on must be installed through the add on installer
on your site, or plone.app.z3cform form macros are not activated.
Running the installer adds a custom browser layer where macros.pt
is hooked as ``ploneform-macros`` view.

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



.. _z3c.form: http://pypi.python.org/pypi/z3c.form
.. _Plone: http://plone.org
.. _plone.z3cform: http://pypi.python.org/pypi/plone.z3cform
