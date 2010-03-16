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

.. _z3c.form: http://pypi.python.org/pypi/z3c.form
.. _Plone: http://plone.org
.. _plone.z3cform: http://pypi.python.org/pypi/plone.z3cform
