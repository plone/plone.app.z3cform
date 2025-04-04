Changelog
=========

.. You should *NOT* be adding new change log entries to this file.
   You should create a file in the news directory instead.
   For helpful instructions, please see:
   https://github.com/plone/plone.releaser/blob/master/ADD-A-NEWS-ITEM.rst

.. towncrier release notes start

4.7.5 (2025-04-04)
------------------

Bug fixes:


- Fix missing `_formater` value for `TimeWidget`.  @petschki (#222)


4.7.4 (2025-03-17)
------------------

Bug fixes:


- Check for `required` on widget instead on field.
  This makes it possible to override it in `updateWidgets` if you have
  complex widgets inside fields.
  [petschki] (#221)


4.7.3 (2025-03-11)
------------------

Bug fixes:


- Fix deprecated `plone_settings` adapter.
  [petschki] (#219)


4.7.2 (2025-01-24)
------------------

Bug fixes:


- Fix DeprecationWarnings. [maurits] (#4090)


4.7.1 (2024-11-25)
------------------

Bug fixes:


- Fix pattern options for `LinkWidget`.
  [petschki] (#213)


4.7.0 (2024-09-24)
------------------

New features:


- Implement new `ContentBrowserWidget` for `pat-contentbrowser` pattern.

  The deprecated `RelatedItemsWidget` and `pat-relateditems` pattern is still available
  and imports should not break. But the default widget and converter adapter registration for
  z3c.relationfield is changed to the new widget.

  Since `plone.app.relationfield` defines the widget with `plone.autoform` schema
  hints nothing changes until the package is updated to the new widget.
  [petschki] (#197)


4.6.1 (2024-05-30)
------------------

Internal:


- Date/time widget: Fix data converter adaption.
  Get the data converter for the date and datetime widgets via adaption and remove the _converter attribute hack.
  This aligns the code to z3c.form standards and allows to override the data converter which was previously not easily possible.
  [thet] (#204)


4.6.0 (2024-04-22)
------------------

New features:


- Use label_css_class attribute from widget if available in checkbox_input & radio_input
  [MrTango] (#202)


4.5.0 (2024-03-19)
------------------

New features:


- Add support for the "accept" attribute on file inputs.

  If the widget's field - if there is one - has the "accept" attribute set (the
  `NamedImage` field has `image/*` set by default) then this is rendered as an
  `accept` attribute on the file input.

  This would restrict the allowed file types before uploading while still being
  checked on the server side.

  Fixes: https://github.com/plone/plone.formwidget.namedfile/issues/66
  Depends on:
  - https://github.com/plone/plone.namedfile/pull/158
  - https://github.com/plone/plone.formwidget.namedfile/pull/67
  [thet] (#198)


Bug fixes:


- Fix `SelectFieldWidget` factory call.
  [petschki] (#192)


4.4.1 (2024-02-27)
------------------

Bug fixes:


- Add missing ``pattern_options`` multiadapter to new PatternFormElement base class.
  [petschki] (#190)
- Implement missing PasswordWidget adapter.
  [petschki] (#193)


4.4.0 (2023-10-18)
------------------

New features:


- Add `row` container to enable column layouts for fields with `wrapper_css_class`.
  [petschki] (#158)
- Implement new ``z3c.form`` extensible attributes feature and cleanup
  widget templates using Chameleon interpolation.
  [petschki] (#181)


Bug fixes:


- Add missing widget configuration for `plone.schema.jsonfield.IJSONField`.
  [petschki] (#185)


4.3.0 (2023-07-14)
------------------

New features:


- Introduce new Email-Widget which is used for `plone.schema.email.IEmail` fields.
  It uses the input type `email`.
  [jensens] (#173)


Bug fixes:


- Fix OrdereSelectWidget browser validation when the input is required.
  [petschki] (#178)
- Ignore form validation when `ignoreRequiredOnExtract` is set.
  [petschki] (#179)


Internal:


- Update configuration files.
  [plone devs] (cfffba8c)


4.2.1 (2023-06-16)
------------------

Bug fixes:


- Add `required` to orderedselect widget.
  [petschki - original PR by szakitibi] (#170)


4.2.0 (2023-05-22)
------------------

New features:


- Move storage utility to plone.namedfile
  to break a dependency cycle between the two.
  [gforcada] (#3764)


Bug fixes:


- Remove invalid unicode control characters for `TextareaWidget`
  [petschki] (#167)


4.1.0 (2023-04-26)
------------------

New features:


- Merge utils and base classes from  ``plone.app.widgets`` and do not depend
  on it anymore. [petschki] (#19)


4.0.3 (2023-04-14)
------------------

Bug fixes:


- Fixes transitive circular dependency to plone.schema.
  Inherit own Browserlayer from new intermediate browserlayer in plone.schema.
  [jensens] (#163)
- Add ``test`` extra with the same contents as the ``tests`` extra.
  The ``tests`` extra will be removed in Plone 7.
  [maurits] (#164)


Internal:


- Update configuration files.
  [plone devs] (3b8337e6)


4.0.2 (2023-03-23)
------------------

Bug fixes:


- Fix relative URLs validation in link widget
  [laulaz] (#160)


Internal:


- Update configuration files.
  [plone devs] (243ca9ec)


4.0.1 (2023-01-26)
------------------

Bug fixes:


- Include ``required`` attribute for ``<textarea>`` fields.
  [frapell] (#156)


4.0.0 (2022-11-30)
------------------

Bug fixes:


- Final release.
  [gforcada] (#600)


4.0.0b1 (2022-08-30)
--------------------

New features:


- Add `default_time` attribute/argument to Date- and DatetimeWidget to allow the converter to set a custom time when nothing was given. [jensens] (#151)
- Customizable DateWidget formatter length.
  [petschki] (#154)


Bug fixes:


- Allow non-default fieldset labels to be translated
  [mtrebron] (#87)
- Fix CSS classname for statusmessage.
  [petschki] (#149)
- Leftovers of Py 2 removed (with pyupgrade and manual edits). then run black & isort.
  Do not depend on CMFPlone any longer (circular dependency), but on plone.base.
  [jensens] (#150)
- Allow DateFieldWidget to be used on schema.datetime. See #151. [jensens] (#151)
- Removed formatting hack for dates before 1900. 
  This was fixed in Python 3.2. 
  [jensens] (#152)


4.0.0a10 (2022-05-24)
---------------------

Bug fixes:


- Re-enable form validation.  [thet] (#147)


4.0.0a9 (2022-04-04)
--------------------

New features:


- Use browser native date and datetime-local input
  together with patternslib date-picker
  [petschki] (#134)
- Use better types for inputs.
  [thet] (#134)
- Remove inlinevalidation from templates.
  [thet] (#134)
- Implement TimeWidget which renders <input type="time" />
  [petschki] (#134)
- Use pat-validation in forms.
  [thet] (#134)


Bug fixes:


- time widget supports 'name' and 'value' attributes now. [iham] (#134)
- Register `AddView` to the correct browserlayer
  [petschki] (#142)


4.0.0a8 (2022-03-23)
--------------------

New features:


- Fixed for latest z3c.form
  [petschki] (#146)


4.0.0a7 (2022-03-09)
--------------------

Bug fixes:


- Add ``name`` attribute to form, if ``view.form_name`` is defined.
  See `easyform issue 325 <https://github.com/collective/collective.easyform/issues/325>`_.
  [maurits] (#325)


4.0.0a6 (2022-01-19)
--------------------

Bug fixes:


- re-enable HTML rendering in form description
  [petschki] (#138)


4.0.0a5 (2022-01-07)
--------------------

Bug fixes:


- Remove erroneous extra curly bracket in class name of the widget wrapper.
  [thet] (#136)


4.0.0a4 (2021-11-26)
--------------------

New features:


- Enable multiple wysiwyg editors (use default editor registry setting) [duchenean, gotcha] (#45)
- Enable formautofocus for Plone forms.
  Allow disabling for specific forms with ``enable_autofocus = False``.
  [jmevissen] (#135)


4.0.0a3 (2021-10-13)
--------------------

Bug fixes:


- Fix form-error alert for BS5 (including invariants errors). [jensens] (#129)
- Fix widget display mode for Bootstrap 5. [jensens] (#130)


4.0.0a2 (2021-09-01)
--------------------

New features:


- Add support for more widget options when working with relation fields. (#125)


4.0.0a1 (2021-04-21)
--------------------

Breaking changes:


- Update form widget implementation for Plone 6 with Bootstrap markup
  [petschki, balavec, agitator] (#127)


New features:


- - Added Exception for ValueError if value is (None,) and term_value can't be set [wkbkhard] (#121) (#121)


Bug fixes:


- Clean up rst documentation titles, spacing, add .vscode and .idea to gitignore.
  [balavec] (#0)


3.2.2 (2020-08-21)
------------------

Bug fixes:


- Fixed repeat syntax in multi input to also work in Zope 4.5.
  [maurits] (#116)


3.2.1 (2020-06-30)
------------------

Bug fixes:


- Fix message type like Error not translated in add form.
  This closes https://github.com/plone/Products.CMFPlone/issues/3126
  [vincentfretin] (#115)


3.2.0 (2020-04-20)
------------------

New features:


- Add display template for RelatedItemsWidget. No longer only render uuids.
  [pbauer] (#111)


3.1.3 (2019-10-12)
------------------

Bug fixes:


- - Fix LinkWidget selected tab on edit #108
    [mamico] (#108)


3.1.2 (2019-08-29)
------------------

Bug fixes:


- Fix wrong default for method attribute in pt
  [mamico] (#107)


3.1.1 (2019-06-27)
------------------

Bug fixes:


- - Fixes: Keywords broken plone/Products.CMFPlone#2885
    [jensens] (#105)


3.1.0 (2019-05-01)
------------------

New features:

- Add display template for AjaxSelectWidget showing the actual vocabularies term title.
  [jensens]

- ``IFieldPermissionChecker`` was moved here from plone.app.widgets.
  [jensens]

Bug fixes:

- Fixes AjaxSelectWidget to respect tokens different from values in vocabularies.
  This includes changes in both, the converter and the widget itself.
  A test was added too.
  ``get_ajaxselect_options`` from ``plone.app.widgets.utils`` is assimilated by the widget now too simplify the whole code,
  so the one in the other package is dead code now and will be deprecated there.
  [jensens]

- LinkFieldWidget: added converter method toFieldValue [ksuess]


3.0.9 (2019-01-08)
------------------

Bug fixes:

- a11y: added role attribute for portalMessage
  [nzambello]


3.0.8 (2018-11-29)
------------------

New features:

- Add support for rendering <optgroup> elements from
  zope.schema.interfaces.ITreeVocabulary hierarchical terms.
  [rpatterson]


3.0.7 (2018-11-07)
------------------

Bug fixes:

- Fix deprecation warning
  (https://github.com/plone/Products.CMFPlone/issues/2605) [ale-rt]


3.0.6 (2018-09-27)
------------------

Bug fixes:

- Prepare for Python 2 / 3 compatibility
  [pbauer, MatthewWilkes, ale-rt]


3.0.5 (2018-06-19)
------------------

Bug fixes:

- Cleanup code analysis problems.
  [jensens]

- Fix SingleCheckBoxBoolWidget description to render structure
  [allusa]

- Prepare for Python 2 / 3 compatibility
  [pbauer, MatthewWilkes, ale-rt]

- Render mimetype selection box correctly for a ``RichTextWidget`` which also
  brings back the TinyMCE.
  [sallner]

- Allow RelatedItems widget to be used in subforms
  [tomgross]

3.0.4 (2018-02-04)
------------------

Bug fixes:

- Fix test failures from https://github.com/plone/plone.app.widgets/pull/177
  [thet]

- Prepare for Python 2 / 3 compatibility
  [pbauer]


3.0.3 (2017-11-24)
------------------

New features:

- Link widget: add ``placeholder`` attributes for external and email link input fields.
  [thet]

Bug fixes:

- Fix: Add missing i18n-domains to templates.
  [jensens]

- Use RichTextValue's output_relative_to(self.context) in RichTextWidget so the ITransform doesn't use siteroot.
  [jaroel]

- Fix in link widget data converter for ``toWidgetValue`` to return an empty structure when the field value is empty instead of returning the portal root object.
  Fixes: https://github.com/plone/Products.CMFPlone/issues/2163
  [thet]

- Keep "internal" links with query strings as external links, otherwise
  the query string is lost
  [tomgross]

- Allow an additional CSS class for widgets in this package
  [tomgross]

- Document customization of widgets
  [tomgross]

3.0.2 (2017-09-06)
------------------

Bug fixes:

- Test fixes for changes in plone.app.widgets querystring options.
  [thet]


3.0.1 (2017-07-03)
------------------

New features:

- Add new and enhanced link widget.
  [tomgross, thet]

Bug fixes:

- Fix broken ``get_tinymce_options`` when called with non-contentish contexts like form or field contexts.
  [thet]

- Related Items Widget: In search mode, when no basePath was set, search site-wide.
  Fixes: https://github.com/plone/mockup/issues/769
  [thet]

- Fixes #64: SingleCheckBoxFieldWidget does not render value in view mode.
  In order to fix this issue the hacky view was removed.
  It is replaced by a new widget to render a single checkbox with bool values.
  An appropriate data converter was added as well.
  [jensens]


3.0 (2017-03-28)
----------------

Breaking changes:

- Removed ``plone.app.z3cform.object`` and
  ``plone.app.z3cform.objectsubform`` because z3c.form 3.3 removed the
  underlying code.
  See https://github.com/zopefoundation/z3c.form/pull/38 for upstream changes.
  [maurits]

New features:

- Add new class ``view-name-VIEWNAME`` to form element indicating the view name w/o old kss prefix.
  New class's replaces ``++`` in view by ``-`` in order to produce valid class (CSS selectable) names.
  [jensens]

Bug fixes:

- Catch TypeError occurring on conflicting subrequests in inline validation
  [tomgross]

- Clean up: code-style, zca-decorators, replace lambda.
  [jensens]


2.2.1 (2017-02-12)
------------------

New features:

- Do not show the "Clear" button for required Date or DateTime fields.
  [thet]

Bug fixes:

- Test fixes for plone.app.widgets 2.1.
  [thet]

- remove deprecated __of__ for browserviews
  [pbauer]


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

- Fix RelatedItemsDataConverter with choice lists, where choices are UUID
  strings of selected relations, but conversion failed, because Choice
  field has None as its value_type
  [datakurre]


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

- Support functions as values in the ``pattern_options`` dictionary, which gets then serialized to JSON.
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
- Fixed checkbox inline validation.
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
