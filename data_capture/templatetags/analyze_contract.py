import math
from urllib.parse import urlencode
from itertools import chain, combinations
from functools import cmp_to_key

try:
    import nltk
except ImportError:
    nltk = None

from django import template
from django.db import connection
from django.db.models import Avg, StdDev
from django.template.loader import render_to_string

from contracts.models import Contract
from contracts.models import EDUCATION_CHOICES as _EDUCATION_CHOICES


# TODO: This is copied from fake_schedule.py, we should probably
# consolidate it somewhere more common.

EDU_LEVELS = {}

for _code, _name in _EDUCATION_CHOICES:
    EDU_LEVELS[_name] = _code

del _code
del _name

register = template.Library()


# https://docs.python.org/3/library/itertools.html#itertools-recipes
def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))


def get_best_permutations(vocab, lexemes, min_count=1, min_length=4,
                          max_permutations=8):
    def compare(a, b):
        a_len = len(a)
        b_len = len(b)

        if a_len != b_len:
            return a_len - b_len

        return vocab_val(a) - vocab_val(b)

    def vocab_val(iterable):
        if len(iterable) == 1:
            return vocab[iterable[0]]
        upper_bound = float('inf')
        for a, b in combinations(iterable, 2):
            c = vocab.get_cooccurrences(a, b)
            if c < upper_bound:
                upper_bound = c
        return upper_bound

    def are_cooccurrences_valid(lexemes):
        for a, b in combinations(lexemes, 2):
            if vocab.get_cooccurrences(a, b) < min_count:
                return False
        return True

    # Remove the first element, as it's the empty set.
    permutations = list(powerset(lexemes))[1:]

    permutations = list(filter(
        lambda x: len(' '.join(x)) >= min_length,
        permutations
    ))
    permutations = list(filter(are_cooccurrences_valid, permutations))
    permutations.sort(key=cmp_to_key(compare), reverse=True)

    return permutations[:max_permutations]


class Vocabulary(dict):
    def __init__(self):
        super()
        self._cinfo = {}

    @classmethod
    def from_list(cls, docs):
        vocab = cls()
        for doc in docs:
            words = doc.split()
            for word in words:
                if word not in vocab:
                    vocab[word] = 0
                vocab[word] += 1
            vocab._update_cooccurrence_info(words)
        return vocab

    @classmethod
    def from_db(cls, cursor, model=Contract, field='search_index',
                min_ndoc=100):
        tsvector_query = 'select {} from {}'.format(
            model._meta.get_field(field).column,
            model._meta.db_table
        )
        cursor.execute(
            "select word, ndoc from ts_stat(%s) WHERE ndoc > %s",
            [tsvector_query, min_ndoc]
        )
        vocab = cls()
        for word, ndoc in cursor.fetchall():
            vocab[word] = ndoc
        vocab._init_cooccurrence_info_from_db(cursor, model, field)
        return vocab

    def get_cooccurrences(self, a, b):
        return self._cinfo.get(a, {}).get(b, 0)

    def _update_cooccurrence_info(self, lexemes):
        cinfo = self._cinfo
        lexemes = [lexeme for lexeme in lexemes if lexeme in self]
        for lexeme in lexemes:
            if lexeme not in cinfo:
                cinfo[lexeme] = {}
            lexeme_cinfo = cinfo[lexeme]
            for other_lexeme in lexemes:
                lexeme_cinfo[other_lexeme] = lexeme_cinfo.get(
                    other_lexeme,
                    0
                ) + 1

    def _init_cooccurrence_info_from_db(self, cursor, model, field):
        with connection.cursor() as cursor:
            cursor.execute('select strip({}) from {}'.format(
                model._meta.get_field(field).column,
                model._meta.db_table
            ))

            for (search,) in cursor:
                lexemes = [lexeme[1:-1] for lexeme in search.split(' ')]
                self._update_cooccurrence_info(lexemes)


def get_lexemes(cursor, words, cache):
    uncached_words = [word for word in words if word not in cache]
    if uncached_words:
        cursor.execute(
            "select {}".format(
                ', '.join(["plainto_tsquery(%s)"] * len(words))
            ),
            words
        )
        lexemes = [column[1:-1] for column in cursor.fetchone()]
        for word, lexeme in zip(words, lexemes):
            cache[word] = lexeme
    return [cache[word] for word in words]


def filter_and_sort_lexemes(vocab, lexemes):
    lexemes = [lexeme for lexeme in lexemes if lexeme in vocab]
    lexemes.sort(
        key=lambda x: vocab[x],
        reverse=True
    )
    return lexemes


class PartOfSpeechMapper:
    def __init__(self, words):
        self._tags = {}
        if nltk is not None:
            self._tags.update(dict(nltk.pos_tag(
                [word.lower() for word in words] +
                # NLTK's POS tagger expects full sentences, whereas the
                # words we've been given really just represent a noun, so
                # we'll use them as the subject of a sentence.
                ['jumps', 'over', 'the', 'lazy', 'dog', '.']
            )))

    def contains_noun(self, words):
        pos_types = [self._tags.get(word.lower(), 'NN') for word in words]
        for pos_type in pos_types:
            if pos_type.startswith('NN'):
                return True
        return False


def broaden_query(cursor, vocab, query, cache, min_count):
    '''
    Return an iterator that yields subsets of the given query; the
    subsets are defined by removing search terms in order of the number of
    documents they appear in, with the most uncommon terms being removed
    first.
    '''

    orig_words = query.split()
    orig_word_ordering = dict(zip(orig_words, range(len(orig_words))))
    orig_lexemes = get_lexemes(cursor, orig_words, cache)
    word_map = dict(zip(orig_lexemes, orig_words))
    lexemes_in_vocab = [lexeme for lexeme in orig_lexemes if lexeme in vocab]
    pos_mapper = PartOfSpeechMapper(orig_words)

    for lexemes in get_best_permutations(vocab, lexemes_in_vocab, min_count):
        words = sorted(
            [word_map[lexeme] for lexeme in lexemes],
            key=lambda word: orig_word_ordering[word]
        )
        if pos_mapper.contains_noun(words):
            yield ' '.join(words)


def find_comparable_contracts(cursor, vocab, labor_category,
                              min_years_experience, education_level,
                              min_count=30, experience_radius=2,
                              cache=None):
    if cache is None:
        cache = {}

    for phrase in broaden_query(cursor, vocab, labor_category, cache,
                                min_count):
        no_results_key = ('find_comparable_contracts:no_results',
                          phrase, min_years_experience, education_level,
                          min_count, experience_radius)
        if no_results_key in cache:
            continue

        contracts = Contract.objects.all().multi_phrase_search(phrase)
        contracts = contracts.filter(
            min_years_experience__gte=min_years_experience - experience_radius,
            min_years_experience__lte=min_years_experience + experience_radius,
            education_level=education_level
        )

        count = contracts.count()
        if count >= min_count:
            return phrase, contracts, count
        else:
            cache[no_results_key] = True
    return None, None, None


def get_data_explorer_url(query, min_experience, max_experience, education):
    # TODO: Use url mapper to get URL for the data explorer.

    params = {
        'q': query,
        'min_experience': min_experience,
        'max_experience': max_experience,
        'education': education
    }

    return '/?{}'.format(urlencode(params))


def describe(cursor, vocab, labor_category, min_years_experience,
             education_level, price, severe_stddevs=2, experience_radius=2,
             cache=None):
    if cache is None:
        cache = {}

    result = {
        'severe': False,
        'description': ''
    }

    phrase, contracts, count = find_comparable_contracts(
        cursor,
        vocab,
        labor_category,
        min_years_experience,
        education_level,
        experience_radius=experience_radius,
        cache=cache
    )

    if contracts is not None:
        wage_field = 'current_price'
        stats = contracts.aggregate(
            avg=Avg(wage_field),
            stddev=StdDev(wage_field)
        )
        avg = stats['avg']
        stddev = stats['stddev']

        price_delta = abs(price - avg)

        if price_delta >= severe_stddevs * stddev:
            result['severe'] = True

        result['count'] = count
        result['avg'] = avg
        result['stddev'] = stddev
        result['stddevs'] = math.ceil(price_delta / stddev)
        result['preposition'] = \
            'w' + ('a' * result['stddevs']) + 'y ' + \
            ('below' if price < avg else 'above')
        result['labor_category'] = phrase
        result['url'] = get_data_explorer_url(
            phrase,
            min_years_experience - experience_radius,
            min_years_experience + experience_radius,
            education_level
        )
        result['description'] = render_to_string(
            'data_capture/analyze_contract.html',
            result
        )

    return result


@register.assignment_tag(takes_context=True)
def analyze_r10_row(context, row):
    # TODO: Currently this only works w/ region 10 schedule rows. Should
    # figure out how to make it work independent of schedules.

    if (row['price_including_iff'].errors or
            row['min_years_experience'].errors or
            row['education_level'].errors or
            row['labor_category'].errors):
        return None

    if '__analyze_contract' not in context:
        # Cache our DB connection and vocabulary so that every time we're
        # run on a row, we're not rebuilding stuff from scratch.
        cursor = connection.cursor()
        vocab = Vocabulary.from_db(cursor)
        context['__analyze_contract'] = (cursor, vocab)

    cursor, vocab = context['__analyze_contract']

    return describe(
        cursor,
        vocab,
        row['labor_category'].value(),
        int(row['min_years_experience'].value()),
        EDU_LEVELS[row['education_level'].value()],
        float(row['price_including_iff'].value())
    )
