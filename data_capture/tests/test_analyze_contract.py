from unittest import TestCase

from ..templatetags.analyze_contract import get_best_permutations


class AnalyzeContractTests(TestCase):
    def test_get_best_permutations_works(self):
        vocab = {
            'junior': 1,
            'administrative': 2,
            'engineer': 3,
        }

        self.assertEqual(
            get_best_permutations(vocab, ['junior', 'administrative',
                                          'engineer']),
            [('junior', 'administrative', 'engineer'),
             ('administrative', 'engineer'),
             ('junior', 'engineer'),
             ('junior', 'administrative'),
             ('engineer',)]
        )
