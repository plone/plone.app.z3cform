from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.z3cform.tests.layer import PAZ3CForm_INTEGRATION_TESTING
from plone.app.z3cform.widgets.querystring import get_querystring_options
from plone.app.z3cform.widgets.relateditems import get_relateditems_options
from plone.app.z3cform.widgets.richtext import get_tinymce_options

import unittest


class TestQueryStringOptions(unittest.TestCase):
    layer = PAZ3CForm_INTEGRATION_TESTING

    def setUp(self):
        setRoles(self.layer["portal"], TEST_USER_ID, ["Contributor"])

    def test__query_string_options(self):
        """Test query string options on root:
        All URLs and paths equal root url and path,
        no favorites
        """

        portal = self.layer["portal"]
        options = get_querystring_options(portal, "@@qsOptions")

        # Test base options
        self.assertEqual(options["indexOptionsUrl"], "http://nohost/plone/@@qsOptions")

        self.assertEqual(
            options["previewCountURL"],
            "http://nohost/plone/@@querybuildernumberofresults",
        )

        self.assertEqual(
            options["previewURL"], "http://nohost/plone/@@querybuilder_html_results"
        )

        # Test options of the AJAX select widget
        self.assertEqual(options["patternAjaxSelectOptions"]["separator"], ";")

        # Test options of the date picker
        self.assertEqual(
            options["patternDateOptions"],
            {
                "behavior": "native",
                "week-numbers": "show",
                "first-day": 0,
                "today": "Today",
                "clear": "Clear",
            },
        )

        # Test options of the related items widget
        self.assertEqual(options["patternRelateditemsOptions"]["basePath"], "/plone")
        self.assertTrue("recentlyUsed" not in options["patternRelateditemsOptions"])


class TestRelatedItemsOptions(unittest.TestCase):
    layer = PAZ3CForm_INTEGRATION_TESTING

    def setUp(self):
        setRoles(self.layer["portal"], TEST_USER_ID, ["Contributor"])

    def test__base_relateditems_options(self):
        """Test related items options on root:
        All URLs and paths equal root url and path,
        no favorites
        """

        portal = self.layer["portal"]
        options = get_relateditems_options(
            portal, None, "#!@", "test_vocab", "@@vocab", "testfield"
        )

        # vocab is correctly set
        self.assertTrue(
            "@@vocab?name=test_vocab&field=testfield" in options["vocabularyUrl"]
        )

        # rootUrl contains something
        self.assertTrue(bool(options["rootUrl"]))

        root_path = context_path = "/".join(portal.getPhysicalPath())
        root_url = context_url = portal.absolute_url()

        # context_path contains something, otherwise this test is meaningless
        self.assertTrue(bool(context_path))
        # context_url contains something, otherwise this test is meaningless
        self.assertTrue(bool(context_url))

        self.assertEqual(options["rootUrl"], root_url)

        self.assertEqual(options["rootPath"], root_path)

        self.assertEqual(
            options["vocabularyUrl"],
            root_url + "/@@vocab?name=test_vocab&field=testfield",
        )

        self.assertEqual(options["basePath"], context_path)

        self.assertEqual(options["contextPath"], context_path)

        self.assertEqual(options["separator"], "#!@")

        self.assertTrue("favorites" not in options)

        # Recently used is configured, but off per default.
        self.assertEqual(options["recentlyUsed"], False)
        self.assertEqual(
            options["recentlyUsedKey"],
            "relateditems_recentlyused_testfield_" + TEST_USER_ID,
        )

    def test__subfolder_relateditems_options(self):
        """Test related items options on subfolder:
        Vocab called on root, start path is folder, have favorites.
        """

        portal = self.layer["portal"]
        portal.invokeFactory("Folder", "sub")
        sub = portal.sub
        options = get_relateditems_options(
            sub, None, "#!@", "test_vocab", "@@vocab", "testfield"
        )

        # vocab is correctly set
        self.assertTrue(
            "@@vocab?name=test_vocab&field=testfield" in options["vocabularyUrl"]
        )

        # rootUrl contains something
        self.assertTrue(bool(options["rootUrl"]))

        root_path = "/".join(portal.getPhysicalPath())
        root_url = portal.absolute_url()
        context_path = "/".join(sub.getPhysicalPath())
        context_url = sub.absolute_url()

        # context_path contains something, otherwise this test is meaningless
        self.assertTrue(bool(context_path))
        # context_url contains something, otherwise this test is meaningless
        self.assertTrue(bool(context_url))

        self.assertEqual(options["rootUrl"], root_url)

        self.assertEqual(options["rootPath"], root_path)

        self.assertEqual(
            options["vocabularyUrl"],
            root_url + "/@@vocab?name=test_vocab&field=testfield",
        )

        self.assertEqual(options["basePath"], context_path)

        self.assertEqual(options["contextPath"], context_path)

        self.assertEqual(options["separator"], "#!@")

        self.assertEqual(len(options["favorites"]), 2)

        self.assertEqual(sorted(options["favorites"][0].keys()), ["path", "title"])

    def test__subdocument_relateditems_options(self):
        """Test related items options on subdoc:
        Vocab called on root, start path is root as document is not folderish,
        no favorites.
        """

        portal = self.layer["portal"]
        portal.invokeFactory("Document", "sub")
        sub = portal.sub
        options = get_relateditems_options(
            sub, None, "#!@", "test_vocab", "@@vocab", "testfield"
        )

        # vocab is correctly set
        self.assertTrue(
            "@@vocab?name=test_vocab&field=testfield" in options["vocabularyUrl"]
        )

        # rootUrl contains something
        self.assertTrue(bool(options["rootUrl"]))

        root_path = "/".join(portal.getPhysicalPath())
        root_url = portal.absolute_url()
        context_path = "/".join(sub.getPhysicalPath())
        context_url = sub.absolute_url()

        # context_path contains something, otherwise this test is meaningless
        self.assertTrue(bool(context_path))
        # context_url contains something, otherwise this test is meaningless
        self.assertTrue(bool(context_url))

        self.assertEqual(options["rootUrl"], root_url)

        self.assertEqual(options["rootPath"], root_path)

        self.assertEqual(
            options["vocabularyUrl"],
            root_url + "/@@vocab?name=test_vocab&field=testfield",
        )

        self.assertEqual(options["basePath"], root_path)

        self.assertEqual(options["contextPath"], context_path)

        self.assertEqual(options["separator"], "#!@")

        self.assertTrue("favorites" not in options)


class TestTinyMCEOptions(unittest.TestCase):
    layer = PAZ3CForm_INTEGRATION_TESTING

    def setUp(self):
        setRoles(self.layer["portal"], TEST_USER_ID, ["Contributor"])

    def test__tinymce_options_different_contexts(self):
        """Test if ``get_tinymce_options`` can be called with different
        contexts, including invalid and form contexts.
        """
        request = self.layer["request"]
        portal = self.layer["portal"]
        portal.invokeFactory("Folder", "sub")
        sub = portal.sub

        # TinyMCE on portal context
        options = get_tinymce_options(portal, None, request)
        self.assertEqual(options["relatedItems"]["basePath"], "/plone")

        # TinyMCE on sub folder context
        options = get_tinymce_options(sub, None, request)
        self.assertEqual(options["relatedItems"]["basePath"], "/plone/sub")
