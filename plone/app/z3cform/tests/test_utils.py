import unittest


class TestUnitCallCallables(unittest.TestCase):
    def test_simple(self):
        from plone.app.z3cform.utils import call_callables

        test_in = 1
        test_compare = 1
        test_out = call_callables(
            test_in,
            "funny return value",
        )
        self.assertEqual(test_out, test_compare)

    def test_simple_function(self):
        from plone.app.z3cform.utils import call_callables

        def test_in(x):
            return x

        test_compare = "funny return value"
        test_out = call_callables(
            test_in,
            "funny return value",
        )
        self.assertEqual(test_out, test_compare)

    def test_list(self):
        from plone.app.z3cform.utils import call_callables

        test_in = [1, 2, 3, lambda x: x]
        test_compare = [1, 2, 3, "funny return value"]
        test_out = call_callables(
            test_in,
            "funny return value",
        )
        self.assertEqual(test_out, test_compare)

    def test_tuple(self):
        from plone.app.z3cform.utils import call_callables

        test_in = (1, 2, 3, lambda x: x)
        test_compare = (1, 2, 3, "funny return value")
        test_out = call_callables(
            test_in,
            "funny return value",
        )
        self.assertEqual(test_out, test_compare)

    def test_complex(self):
        from plone.app.z3cform.utils import call_callables

        test_in = {
            "normal": 123,
            "list": [
                1,
                2,
                3,
                lambda x: x,
                [11, 22, 33, lambda x: x, (44, 55, 66, lambda x: x)],
            ],  # noqa
            "tuple": (
                1,
                2,
                3,
                lambda x: x,
                (11, 22, 33, lambda x: x, [44, 55, 66, lambda x: x]),
            ),  # noqa
            "dict": {
                "subnormal": 456,
                "sublist": [4, 5, 6, lambda x: x],
                "subtuple": (4, 5, 6, lambda x: x),
                "subdict": {
                    "subsubnormal": 789,
                    "subsublist": [7, 8, 9, lambda x: x],
                    "subsubtuple": (7, 8, 9, lambda x: x),
                },
            },
        }

        test_compare = {
            "normal": 123,
            "list": [
                1,
                2,
                3,
                "funny return value",
                [11, 22, 33, "funny return value", (44, 55, 66, "funny return value")],
            ],  # noqa
            "tuple": (
                1,
                2,
                3,
                "funny return value",
                (11, 22, 33, "funny return value", [44, 55, 66, "funny return value"]),
            ),  # noqa
            "dict": {
                "subnormal": 456,
                "sublist": [4, 5, 6, "funny return value"],
                "subtuple": (4, 5, 6, "funny return value"),
                "subdict": {
                    "subsubnormal": 789,
                    "subsublist": [7, 8, 9, "funny return value"],
                    "subsubtuple": (7, 8, 9, "funny return value"),
                },
            },
        }

        test_out = call_callables(
            test_in,
            "funny return value",
        )

        self.assertEqual(test_out, test_compare)


class TestUtils(unittest.TestCase):
    def test_is_absolute(self):
        from plone.app.z3cform.utils import is_absolute

        self.assertTrue(is_absolute("https://plone.org/"))
        self.assertTrue(is_absolute("http://plone.org/"))
        self.assertTrue(is_absolute("webdav://plone.org/"))
        self.assertTrue(not is_absolute("./path/to/site"))
        self.assertTrue(not is_absolute("/resolveuid/"))

    def test_is_same_domain(self):
        from plone.app.z3cform.utils import is_same_domain

        # Those use the same protocol and are on the same domaain
        self.assertTrue(
            is_same_domain(
                "https://plone.org/doc1",
                "https://plone.org/doc2/doc3",
            )
        )

        # These are two completely different URLs
        self.assertTrue(
            not is_same_domain(
                "https://domain1.com",
                "https://anotherdomain.com",
            )
        )

        # Here, different transport protocols are used. Returning False.
        self.assertTrue(
            not is_same_domain(
                "https://plone.org",
                "http://plone.org",
            )
        )

    def test_unicode_control_character_removal(self):
        from plone.app.z3cform.utils import remove_invalid_xml_characters

        for x in range(32):
            if x in (9, 10, 13):
                self.assertTrue(remove_invalid_xml_characters(chr(x)) == chr(x))
            else:
                self.assertTrue(remove_invalid_xml_characters(chr(x)) == "")
