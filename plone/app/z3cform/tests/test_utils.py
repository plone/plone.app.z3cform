# -*- coding: utf-8 -*-
import unittest


class TestUnitCallCallables(unittest.TestCase):

    def test_simple(self):
        from plone.app.z3cform.utils import call_callables

        test_in = 1
        test_compare = 1
        test_out = call_callables(
            test_in,
            'funny return value'
        )
        self.assertEqual(test_out, test_compare)

    def test_simple_function(self):
        from plone.app.z3cform.utils import call_callables

        test_in = lambda x: x
        test_compare = 'funny return value'
        test_out = call_callables(
            test_in,
            'funny return value'
        )
        self.assertEqual(test_out, test_compare)

    def test_list(self):
        from plone.app.z3cform.utils import call_callables

        test_in = [1, 2, 3, lambda x: x]
        test_compare = [1, 2, 3, 'funny return value']
        test_out = call_callables(
            test_in,
            'funny return value'
        )
        self.assertEqual(test_out, test_compare)

    def test_tuple(self):
        from plone.app.z3cform.utils import call_callables

        test_in = (1, 2, 3, lambda x: x)
        test_compare = (1, 2, 3, 'funny return value')
        test_out = call_callables(
            test_in,
            'funny return value'
        )
        self.assertEqual(test_out, test_compare)

    def test_complex(self):
        from plone.app.z3cform.utils import call_callables

        test_in = {
            'normal': 123,
            'list': [1, 2, 3, lambda x: x, [11, 22, 33, lambda x: x, (44, 55, 66, lambda x: x)]],  # noqa
            'tuple': (1, 2, 3, lambda x: x, (11, 22, 33, lambda x: x, [44, 55, 66, lambda x: x])),  # noqa
            'dict': {
                'subnormal': 456,
                'sublist': [4, 5, 6, lambda x: x],
                'subtuple': (4, 5, 6, lambda x: x),
                'subdict': {
                    'subsubnormal': 789,
                    'subsublist': [7, 8, 9, lambda x: x],
                    'subsubtuple': (7, 8, 9, lambda x: x),
                }
            }
        }

        test_compare = {
            'normal': 123,
            'list': [1, 2, 3, 'funny return value', [11, 22, 33, 'funny return value', (44, 55, 66, 'funny return value')]],  # noqa
            'tuple': (1, 2, 3, 'funny return value', (11, 22, 33, 'funny return value', [44, 55, 66, 'funny return value'])),  # noqa
            'dict': {
                'subnormal': 456,
                'sublist': [4, 5, 6, 'funny return value'],
                'subtuple': (4, 5, 6, 'funny return value'),
                'subdict': {
                    'subsubnormal': 789,
                    'subsublist': [7, 8, 9, 'funny return value'],
                    'subsubtuple': (7, 8, 9, 'funny return value'),
                }
            }
        }

        test_out = call_callables(
            test_in,
            'funny return value'
        )

        self.assertEqual(test_out, test_compare)


def test_suite():
    return unittest.TestSuite([
        unittest.makeSuite(TestUnitCallCallables),
    ])
