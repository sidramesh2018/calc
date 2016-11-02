import math
from urllib.parse import urlencode
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


def get_vocab(cursor, model=Contract, field='search_index', min_ndoc=100):
    tsvector_query = 'select {} from {}'.format(
        model._meta.get_field(field).column,
        model._meta.db_table
    )
    cursor.execute(
        "select word, ndoc from ts_stat(%s) WHERE ndoc > %s",
        [tsvector_query, min_ndoc]
    )
    vocab = {}
    for word, ndoc in cursor.fetchall():
        vocab[word] = ndoc
    return vocab


def get_lexemes(cursor, words):
    cursor.execute(
        "select {}".format(
            ', '.join(["plainto_tsquery(%s)"] * len(words))
        ),
        words
    )
    return [column[1:-1] for column in cursor.fetchone()]


def filter_and_sort_lexemes(vocab, lexemes):
    lexemes = [lexeme for lexeme in lexemes if lexeme in vocab]
    lexemes.sort(
        key=lambda x: vocab[x],
        reverse=True
    )
    return lexemes


def broaden_query(cursor, vocab, query):
    '''
    Return an iterator that yields subsets of the given query; the
    subsets are defined by removing search terms in order of the number of
    documents they appear in, with the most uncommon terms being removed
    first.
    '''

    orig_words = query.split()
    orig_word_ordering = dict(zip(orig_words, range(len(orig_words))))
    orig_lexemes = get_lexemes(cursor, orig_words)
    lexeme_map = dict(zip(orig_lexemes, orig_words))
    lexemes = filter_and_sort_lexemes(vocab, orig_lexemes)
    words = [lexeme_map[lexeme] for lexeme in lexemes]

    while words:
        words_copy = words[:]
        words_copy.sort(key=lambda word: orig_word_ordering[word])
        yield ' '.join(words_copy)

        # TODO: Consider iterating over more combinations of
        # terms rather than just popping off the most uncommon one.

        words.pop()


def find_comparable_contracts(cursor, vocab, labor_category,
                              min_years_experience, education_level,
                              min_count=30, experience_radius=2):
    for phrase in broaden_query(cursor, vocab, labor_category):
        contracts = Contract.objects.all().multi_phrase_search(phrase)
        contracts = contracts.filter(
            min_years_experience__gte=min_years_experience - experience_radius,
            min_years_experience__lte=min_years_experience + experience_radius,
            education_level=education_level
        )
        if contracts.count() >= min_count:
            return phrase, contracts
    return None, None


def get_data_explorer_url(query, min_experience, max_experience, education):
    # TODO: Use url mapper to get URL for the data explorer.

    params = {
        'q': query,
        'min_experience': min_experience,
        'max_experience': max_experience,
        'education': education
    }

    return '/?{}'.format(urlencode(params))


def describe(labor_category, min_years_experience, education_level, price):
    result = {
        'severe': False,
        'description': ''
    }

    EXPERIENCE_RADIUS = 2
    SEVERE_STDDEVS = 2

    with connection.cursor() as cursor:
        vocab = get_vocab(cursor)
        phrase, contracts = find_comparable_contracts(
            cursor,
            vocab,
            labor_category,
            min_years_experience,
            education_level,
            experience_radius=EXPERIENCE_RADIUS
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

            if price_delta >= SEVERE_STDDEVS * stddev:
                result['severe'] = True

            url = get_data_explorer_url(
                phrase,
                min_years_experience - EXPERIENCE_RADIUS,
                min_years_experience + EXPERIENCE_RADIUS,
                education_level
            )

            result['description'] = render_to_string(
                'data_capture/analyze_contract.html', {
                    'severe': result['severe'],
                    'stddevs': math.ceil(price_delta / stddev),
                    'labor_category': phrase,
                    'url': url
                }
            )

    return result


@register.filter
def analyze_contract_row(row):
    # TODO: Currently this only works w/ fake schedule rows. Should
    # figure out how to make it work independent of schedules; that
    # might mean abandoning this weird template filter approach.

    if (row['price'].errors or row['years_experience'].errors or
            row['education'].errors or row['service'].errors):
        return None

    return describe(
            row['service'].value(),
            int(row['years_experience'].value()),
            EDU_LEVELS[row['education'].value()],
            float(row['price'].value())
        )
