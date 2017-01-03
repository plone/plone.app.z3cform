Changelog
=========

2.2 (2017-01-02)
----------------

Breaking changes:

- Test fixes for plone.app.widgets 2.1.
  While this is not a breaking change functionality or API wise, the tests do only pass with plone.app.widgets 2.1.
  [thet]

Bug fixes:

- Fix RelatedItemsDataConverter with relation lists, where in an iteration a wrong value was checked to be existent.
  Fixes failures in situations, where a ``None`` value was part of the relation list.
  [thet]


2.1.2 (2016-12-02)
------------------

Bug fixes:

- Remove ZopeTestCase.
  [ivanteoh, maurits]

- In select widget, accept items as property or method.
  This avoids breaking on some z3c.form versions.
  See https://github.com/zopefoundation/z3c.form/issues/44
  [maurits]


2.1.1 (2016-09-16)
------------------

Bug fixes:

- Enable unload protection by using pattern class ``pat-formunloadalert`` instead ``enableUnloadProtection``.
  [thet]


2.1 (2016-08-12)
----------------

New features:

- Related items data converter supports explicit value_type specified in
  field when using collections of UUID values.  This is backward-compatible
  with previous conversion to field values, supports str/unicode value(s),
  whichever is specified by field.
  [seanupton]

- Support functions as values in the ``pattern_options`` dictionary, whch gets then serialized to JSON.
  Before that, walk recursively through ``pattern_options`` and call all functions with the widgets context.
  This allows for context-specific, runtime evaluated pattern option values.
  [thet]

- Don't overwrite widget default css classes when rendering pattern widgets.
  This allows setting a css class via the ``klass`` keyword in plone.autoform widget directives.
  [thet]


2.0.0 (2016-04-29)
------------------

Incompatibilities:

- Deprecated "plone.app.z3cform.object" and moved to
  "plone.app.z3cform.objectsubform" in order to avoid built in names
  as module names, which may result in difficult to debug errors.
  [jensens]

- Made existing soft deprecation (by comment) of plone.app.z3cform.layout
  explicit by deprecating using zope.deferredimport.
  [jensens]

- removed plone.app.z3cform.queryselect since this was deprecated already
  and removal planned (!) already for Plone 4.1
  [jensens]

New:

- make widget available to wysiwyg_support template
  [gotcha]

Fixes:

- Reduce dependency on plone.app.widgets in tests.
  [thet]

- Enhance test in order to show problem in RelatedItemsWidget with
  navigation-roots
  [jensens]

- Cleanup: pep8, uth8-headers, zca-decorators, ...
  [jensens]


1.2.0 (2016-02-25)
------------------

New:

- Add metal slot for inserting stuff below fields
  [fredvd]

Fixes:

- Fix ajax selection for add forms
  [tomgross]

- Use doctest instead of zope.testing.doctest
  [pbauer]

- Fix related items widget tests to include root path support.
  Fix options merging for TinyMCE widget.
  [alecm]

- Fixed test for plone.app.widgets.
  [Gagaro]

- Used assertDictEqual instead of assertEqual for RelatedItemsWidgetTests.test_widget
  [Gagaro]

1.1.8 (2016-01-08)
------------------

Fixes:

- Fixed tests for newer CMFPlone.  [Gagaro, ebrehault, vangheem]


1.1.7 (2015-11-26)
------------------

Fixes:

- Don't allow adding new terms in the AjaxAutocompleteWidget
  when it's used with a Choice field.
  [davisagli]

- Remove installation of plone.app.widgets default profile. In Plone 5 with
  plone.app.widgets >= 2.0, the profile is only a dummy profile for BBB
  compatibility.
  [thet]


1.1.6 (2015-10-27)
------------------

Fixes:

- Check if user can add keywords for AjaxSelectWidget.
  [Gagaro]


1.1.5 (2015-09-20)
------------------

- Don't check portal_registry for default_charset, we only accept
  utf-8.
  [esteele]

- Allow time options to be customized for DatetimeWidget.
  [thet]

- Wrap context to allow tools to be found in text widget.
  [cguardia]


1.1.4 (2015-09-16)
------------------

- Remove unittest2 dependency.
  [gforcada]


1.1.3 (2015-07-18)
------------------

- Also mock getToolByName for some tests.
  [vangheem]


1.1.2 (2015-05-11)
------------------

- grab selected editor from user
  [vangheem]


1.1.1 (2015-05-04)
------------------

- Use the more specific browser layer ``IPloneFormLayer`` for adapter
  registrations. This avoids double registration errors.
  [thet]


1.1.0 (2015-03-21)
------------------

- Integrate plone.app.widgets.
  [vangheem]


1.0.2 (unreleased)
------------------

- Fix inline-validation warning error
  [jbirdwell]


1.0.1 (2014-10-23)
------------------

- Handle an error where group.__name__ being None caused fieldsets to be given
  the id 'fieldset-none', which causes issues the inline validation.
  [esteele]


1.0 (2014-02-26)
----------------

- Remove dependency on collective.z3cform.datetimewidget and instead use
  plone.app.widgets.
  [garbas, thet]


0.7.6 (2014-01-27)
------------------

- Translate fieldset labels correctly.
  [maurits]

- We can add enable_unload_protection = False on a Form to disable unload protection.
  [thomasdesvenain]

- Add '.empty' css class to fields that have no value.
  [cedricmessiant]

- Indicate 'error' status when reporting errors from group forms.
  [davisagli]

- Replace deprecated test assert statements.
  [timo]

- Solve #13567: InlineValidation broken for MultiWidget.
  [sunew]


0.7.5 (2013-10-09)
------------------

- Fix an issue with the inline validator, KSS was giving values for
  fieldset attr than can't be converted to an integer.
  [jpgimenez]
- Inline validation supports fieldset names instead of integer-indexed naming.
  [seanupton]
- Use group __name__, not label value to have stable fieldset_name used in
  DOM id, and for inline validation.
  [seanupton]
- Inline validation robustness if no field name is passed by client request.
  [seanupton]
- Support for IDict in the MultiWidget. Makes it compatible with z3c.form 3.0 (released 2013-06-24)
  [djay]
- Give fieldset legends ids based on their name, for compatibility with
  Archetypes.
  [davisagli]
- Fixed chechbox inline validation.
  [kroman0]


0.7.4 (2013-08-13)
------------------

- Display 'required' span only on input mode.
  [cedricmessiant]


0.7.3 (2013-05-23)
------------------

- Added possibility to use z3c.form's ContentProviders [gbastien, jfroche, gotcha]


0.7.2 (2013-03-05)
------------------

- Add a macro and slot to the @@ploneform-render-widget templates
  so it's possible to override the widget rendering without
  changing the markup surrounding it.
  [davisagli]

- Restored support for contents without acquisition chain
  [keul]


0.7.1 (2013-01-01)
------------------


- Overrode ObjectSubForm for IObject field in order to provide get_closest_content
  method. Now it is possible to guess the closest content from a Multiwidget subform.
  [gborelli]

- Added utils.closest_content from plone.formwidget.contenttree.utils
  [gborelli]

- Primarily use form name for 'kssattr-formname' form attribute.
  [vipod]

- Rename the 'fieldset.current' hidden input to 'fieldset' for consistency
  with Archetypes.
  [davisagli]


0.7.0 (2012-10-16)
------------------

- Support inline validation without depending on KSS.
  [davisagli]

- Fix a case where the widget broke if its form's content was a dict.
  [davisagli]


0.6.1 (2012-08-30)
------------------

- Fix the single checkbox widget to cope with widgets with a __call__ method.
  [davisagli]


0.6.0 (2012-05-25)
------------------

- Remove hard-coded &#x25a0; (box) markers from required labels to match
  changes made in sunburst/public.css and archetypes. Fixes double required
  markers in Plone 4.2rc1.

- Pull form help inside label tag and make it a span rather than a div. The
  purpose is to improve accessibility by making the semantic connection between
  label and help. Related to http://dev.plone.org/ticket/7212

- Use ViewPageTemplateFile from zope.browserpage.
  [hannosch]

0.5.8 (2012-05-07)
------------------

- Prevent empty error divs from being generated if errors are already associated
  with a field.
  [davidjb]

0.5.7 - 2011-11-26
------------------

- Corrected formatting for errors on the FieldWidgets object (i.e. from
  invariants). This closes http://code.google.com/p/dexterity/issues/detail?id=238
  [davisagli]

- Added the ``i18n:domain`` attribute in the first ``div`` of ``widget.pt`` in order to make the
  "required" tooltip translatable. Fixes http://dev.plone.org/plone/ticket/12209
  [rafaelbco]

0.5.6 - 2011-06-30
------------------

- Make sure group errors get styled like field errors.
  [davisagli]

- Include group and field descriptions as structure.
  [davisagli]

0.5.5 - 2011-06-26
------------------

- Make it possible to add a custom CSS class to a form by setting its
  ``css_class`` attribute.
  [davisagli]

- Match plone.z3cform's template in including the form description as
  structure.
  [davisagli]

0.5.4 - 2011-05-04
------------------

- Customize templates for multi and object widgets for more consistent styling.
  [elro]

- Remove dependency on zope.app.component.
  [davisagli]

- Add MANIFEST.in.
  [WouterVH]

- Raise LookupError when terms are not found (e.g. they are no longer visible due to security)
  [lentinj]


0.5.3 - 2011-01-22
------------------

- Fix test setup in Zope 2.10.
  [davisagli]


0.5.2 - 2011-01-18
------------------

- Don't use collective.testcaselayer based IntegrationTestLayer as it leads to
  PicklingError on Plone 4.1.
  [elro]

- Change inline validation to match archetypes behavior - add a warning class and
  omit the error message.
  [elro]


0.5.1 - 2010-11-02
------------------

- Make sure form.extractData() does not raise an AttributeError if the method is
  called before the form is available (first page load).
  [timo]

- This package now uses the plone i18n domain.
  [vincentfretin]

- Added option to override <form action="">.
  [miohtama]

- Updated README regarding form action and method.
  [miohtama]


0.5.0 - 2010-04-20
------------------

- Render errors from group form widget manager validators.  Fixes
  http://code.google.com/p/dexterity/issues/detail?id=96
  [davisagli]

- Default to showing the default fieldset, rather than the first non-default
  fieldset.
  [davisagli]

- Replace the required field indicator image with a unicode box, refs
  http://dev.plone.org/plone/ticket/10352
  [davisagli, limi]

- Replaced the existing radiobutton-based boolean widget with the standard
  single checkbox Plone version.
  [limi]

- Add @@ploneform-render-widget view, so that the widget chrome can be
  customized for particular widget types.
  [davisagli]

- Added slots to the ``titlelessform`` macro. See ``README.txt`` in
  ``plone.z3cform`` for details.
  [optilude, davisagli]

- Cleaned up templates to match Plone 4 conventions.
  [optilude]

- Made templates and inline validation work with standalone forms as supported
  by plone.z3cform 0.6 and later.
  [optilude]

- Installed a browser layer IPloneFormLayer with this package's extension
  profile. This inherits from z3c.form's IFormLayer, allowing the default
  widgets to work. You should always install this package in
  portal_quickinstaller before using z3c.form forms in Plone.
  [optilude]

- Made the textlines widget the default for sequence types with text/ascii
  line value types. The default widget from z3c.form is too confusing.
  [optilude]

- Use form method defined in form class. This allows HTTP GET forms.
  Before method was hardcoded to "post" in the template. [miohtama]


0.4.9 - 2010-01-08
------------------

- Remove unused (and broken on Plone 4) lookup of the current user's WYSIWYG
  editor preference.  The wysiwyg_support template does this for us.
  [davisagli]


0.4.8 - 2009-10-23
------------------

- Made the KSS validator use publish traversal instead of OFS traversal to find
  the form. This makes it usable with forms reached by custom IPublishTraverse
  adapters.
  [davisagli]

- Added enable_form_tabbing option to not transform fieldsets into tabs.
  [vincentfretin]

- Added an id to the generated form.
  [vincentfretin]

- Fixed issue in macros.pt: fieldset.current hidden input was never generated.
  [vincentfretin]


0.4.7 - 2009-09-25
------------------

- Set plone i18n domain for "Info" and "Error" messages in macros.pt so they are translated.
  [vincentfretin]


0.4.6 - 2009-07-26
------------------

- Include plone.z3cform's overrides.zcml from our own overrides.zcml.
  [optilude]

- Updated to collective.z3cform.datetimewidget>=0.1a2 to fix a ZCML conflict
  with z3c.form.
  [davisagli]


0.4.5 - 2009-05-25
------------------

- Made the KSS form support conditional on both kss.core and Archetypes being
  installed.
  [hannosch]

- Use the date/time widgets from collective.z3cform.datetimewidget as the default
  widget for Date and Datetime fields.
  [davisagli]


0.4.4 - 2009-05-03
------------------

- Made the KSS validator use traversal instead of getMultiAdapter() to find
  the form. This makes it work on add forms.
  See http://code.google.com/p/dexterity/issues/detail?id=27
  [optilude]


0.4.3 - 2009-04-17
------------------

- Added a display template for the WYSIWYG widget.
  [optilude]

- Make the ?fieldset.current query string variable work. Set it to the id
  of a fieldset other than default to pre-select a different fieldset, e.g.
  .../@@formview?fieldset.current=3
  [optilude]

- Hide the 'default' fieldset if there's nothing to show there.
  [optilude]

- Provide 'portal' variable in wysiwyg template, as its used by some editors.
  [davisagli]


0.4.2 - 2008-09-04
------------------

- Make the WYSIWYG widget work also for non-Acquisition wrapped
  content.


0.4.1 - 2008-08-21
------------------

- Removed maximum version dependency on zope.component. This should be left
  to indexes, known good sets or explicit version requirements in buildouts.
  If you work with zope.component >= 3.5 you will also need five.lsm >= 0.4.
  [hannosch]

- Make use of new plone.z3cform support for looking up the layout template by
  adapter. This means that forms now no longer need to depend on
  plone.app.z3cform unless they want to use Plone-specific widgets.


0.4.0 - 2008-07-31
------------------

- Add inline validation support with KSS

- Require zope.component <= 3.4.0 to prevent compatibility issues with
  five.localsitemanager, of which a buggy version (0.3) is pinned by
  plone.recipe.plone 3.1.4.  Upgrade to this version if you're seeing::

    ...
    Module five.localsitemanager.registry, line 176, in registeredUtilities
    ValueError: too many values to unpack


0.3.2 - 2008-07-25
------------------

- Fixed a bug in macros.pt where 'has_groups' and 'show_default_label'
  for fieldsets were set in the 'form' macro, rendering the 'field'
  macro unusable by itself.


0.3.1 - 2008-07-24
------------------

- Fixed a bug where we would use the form macros defined in
  plone.z3cform instead of our own.


0.3 - 2008-07-24
----------------

- Create this package from Plone-specific bits that have been factored
  out of plone.z3cform.
