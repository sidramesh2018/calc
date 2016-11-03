from unittest import TestCase

from ..templatetags.analyze_contract import get_best_permutations


VOCAB = {
    'junior': 1,
    'administrative': 2,
    'engineer': 3,
    'ii': 4,
}


class GetBestPermutationsTests(TestCase):
    def test_min_length_works(self):
        self.assertEqual(
            get_best_permutations(VOCAB, ['engineer', 'ii'], min_length=3),
            [('engineer', 'ii'),
             ('engineer',)],
        )

    def test_max_permutations_works(self):
        self.assertEqual(
            get_best_permutations(VOCAB, ['junior', 'administrative',
                                          'engineer'], max_permutations=2),
            [('junior', 'administrative', 'engineer'),
             ('administrative', 'engineer')]
        )

    def test_it_works(self):
        self.assertEqual(
            get_best_permutations(VOCAB, ['junior', 'administrative',
                                          'engineer']),
            [('junior', 'administrative', 'engineer'),
             ('administrative', 'engineer'),
             ('junior', 'engineer'),
             ('junior', 'administrative'),
             ('engineer',),
             ('administrative',),
             ('junior',)],
        )
